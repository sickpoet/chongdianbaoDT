/* 国庆旅游热度榜 · 前端逻辑（纯静态，依赖 data.js 的 window.TRAVEL_DATA） */
(function () {
  "use strict";
  var D = window.TRAVEL_DATA;
  if (!D) { document.getElementById("main").innerHTML = '<div class="empty">数据加载失败：未找到 data.js</div>'; return; }

  var PRESSURE = {
    sold_out: { label: "已售罄", cls: "sold_out" },
    tight: { label: "紧张·无折扣", cls: "tight" },
    normal: { label: "正常", cls: "normal" },
    cheap: { label: "价格低位", cls: "cheap" }
  };

  var state = { tab: "actual", q: "", sort: {} };

  function $(s) { return document.querySelector(s); }
  function el(id) { return document.getElementById(id); }
  function esc(s) {
    if (s == null) return "";
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function fmt(v, d) {
    if (v == null) return "—";
    if (typeof v === "number") return v.toLocaleString("zh-CN", { maximumFractionDigits: d == null ? 1 : d });
    return esc(v);
  }
  function yoy(v) {
    if (v == null) return '<span class="muted">—</span>';
    var cls = v > 0 ? "pos" : (v < 0 ? "neg" : "muted");
    var arr = v > 0 ? "▲" : (v < 0 ? "▼" : "");
    return '<span class="' + cls + '">' + arr + Math.abs(v) + "%</span>";
  }
  function rankBadge(n) { return n ? ("第 " + n + " 位") : "—"; }
  function pBadge(level) {
    if (!level) return '<span class="badge dim">—</span>';
    var p = PRESSURE[level] || { label: level, cls: "dim" };
    return '<span class="badge ' + p.cls + '">' + esc(p.label) + "</span>";
  }
  function hit(q, str) { return !q || (str || "").toLowerCase().indexOf(q.toLowerCase()) >= 0; }

  /* ---------------- 子标题 / 说明 ---------------- */
  el("subtitle").textContent =
    "数据更新 " + D.meta.updated + " ｜ 去年：" + D.meta.holiday_2025 + " ｜ 今年：" + D.meta.holiday_2026;
  el("disclaimer").textContent = "口径说明：" + D.meta.disclaimer;

  /* ---------------- 通用表格构建 ---------------- */
  function table(tabId, columns, rows, onRow) {
    var sk = state.sort[tabId];
    if (sk && sk.key) {
      var col = columns.filter(function (c) { return c.key === sk.key; })[0];
      rows = rows.slice().sort(function (a, b) {
        var va = a[sk.key], vb = b[sk.key];
        if (va == null) va = col.num ? -Infinity : "";
        if (vb == null) vb = col.num ? -Infinity : "";
        if (col.num) return sk.dir === "asc" ? va - vb : vb - va;
        return sk.dir === "asc" ? String(va).localeCompare(String(vb), "zh") : String(vb).localeCompare(String(va), "zh");
      });
    }
    var thead = "<tr>" + columns.map(function (c) {
      var sorted = sk && sk.key === c.key;
      var arrow = sorted ? (sk.dir === "asc" ? "▲" : "▼") : "↕";
      return '<th data-key="' + c.key + '" class="' + (sorted ? "sorted" : "") + '">' + esc(c.label) +
        ' <span class="arrow">' + arrow + "</span></th>";
    }).join("") + "</tr>";

    var tbody = rows.map(function (r, i) {
      var tds = columns.map(function (c) {
        var v = c.fmt ? c.fmt(r) : fmt(r[c.key]);
        return "<td" + (c.num ? ' class="num"' : "") + ">" + v + "</td>";
      }).join("");
      return '<tr data-row="' + i + '">' + tds + "</tr>";
    }).join("");

    var html = '<div class="table-scroll"><table><thead>' + thead + "</thead><tbody>" +
      (tbody || '<tr><td colspan="' + columns.length + '" class="muted">无匹配结果</td></tr>') +
      "</tbody></table></div>";

    var wrap = document.createElement("div");
    wrap.innerHTML = html;
    wrap.querySelectorAll("th[data-key]").forEach(function (th) {
      th.addEventListener("click", function () {
        var key = th.getAttribute("data-key");
        var cur = state.sort[tabId];
        if (cur && cur.key === key) cur.dir = cur.dir === "asc" ? "desc" : "asc";
        else state.sort[tabId] = { key: key, dir: "desc" };
        render();
      });
    });
    if (onRow) {
      wrap.querySelectorAll("tbody tr[data-row]").forEach(function (tr) {
        tr.addEventListener("click", function () { onRow(rows[+tr.getAttribute("data-row")]); });
      });
    }
    return wrap;
  }

  function card(title, desc, node, src, id) {
    var c = document.createElement("div");
    c.className = "card";
    if (id) c.id = id;
    c.innerHTML = "<h3>" + esc(title) + "</h3>" + (desc ? '<p class="board-desc">' + esc(desc) + "</p>" : "");
    c.appendChild(node);
    if (src) { var s = document.createElement("div"); s.className = "src"; s.textContent = "来源：" + src; c.appendChild(s); }
    return c;
  }

  /* 参考榜内：带平台来源标题的子区块，避免多平台数据挤在一起 */
  function subSection(title, src, node) {
    var s = document.createElement("div");
    s.className = "sub";
    s.innerHTML = "<h4>" + esc(title) + (src ? ' <span class="sub-src">' + esc(src) + "</span>" : "") + "</h4>";
    s.appendChild(node);
    return s;
  }

  function chips(list, meta, max) {
    var box = document.createElement("div");
    box.className = "chips";
    (max ? list.slice(0, max) : list).forEach(function (name, i) {
      var c = document.createElement("span");
      c.className = "chip";
      c.innerHTML = "<b>" + (i + 1) + ".</b> " + esc(name) + (meta ? ' <span class="rk">' + esc(meta) + "</span>" : "");
      box.appendChild(c);
    });
    return box;
  }

  /* ---------------- 各榜单 ---------------- */
  function renderActual() {
    var main = el("main");
    var q = state.q;
    var cities = D.cities.filter(function (c) { return c.has_2025 && hit(q, c.city + c.province); })
      .sort(function (a, b) { return b.visits_wan - a.visits_wan; });
    var provs = D.provinces_2025.filter(function (p) { return hit(q, p.province); })
      .sort(function (a, b) { return b.visits_wan - a.visits_wan; });

    var cityCols = [
      { key: "city", label: "城市", fmt: function (r) { return esc(r.city); } },
      { key: "province", label: "省份", fmt: function (r) { return esc(r.province); } },
      { key: "visits_wan", label: "接待(万人次)", num: true, fmt: function (r) { return fmt(r.visits_wan, 0); } },
      { key: "visits_yoy", label: "同比", fmt: function (r) { return yoy(r.visits_yoy); } },
      { key: "revenue_yi", label: "旅游收入(亿)", num: true, fmt: function (r) { return fmt(r.revenue_yi, 1); } },
      { key: "per_capita", label: "人均(元)", num: true, fmt: function (r) { return fmt(r.per_capita, 0); } },
      { key: "scope", label: "统计口径", fmt: function (r) { return esc(r.scope || "—"); } }
    ];
    var provCols = [
      { key: "province", label: "省份", fmt: function (r) { return esc(r.province); } },
      { key: "visits_wan", label: "接待(万人次)", num: true, fmt: function (r) { return fmt(r.visits_wan, 0); } },
      { key: "visits_yoy", label: "同比", fmt: function (r) { return yoy(r.visits_yoy); } },
      { key: "revenue_yi", label: "旅游收入(亿)", num: true, fmt: function (r) { return fmt(r.revenue_yi, 1); } },
      { key: "per_capita", label: "人均(元)", num: true, fmt: function (r) { return fmt(r.per_capita, 0); } }
    ];

    main.innerHTML = "";
    main.appendChild(card(
      "城市接待量 Top（2025 国庆中秋实际）",
      "去年国庆哪些城市人流量最高——按全市接待人次排序，点击行看详情。",
      table("actual-city", cityCols, cities, openCity),
      "各地文旅局", "actual-city"
    ));
    main.appendChild(card(
      "省份接待量 Top（2025）",
      "部分省份未单列城市口径，跨城比较仅供参考。",
      table("actual-prov", provCols, provs),
      "30 省份文旅成绩单", "actual-prov"
    ));

    if (D.cities_2025_partial && D.cities_2025_partial.length && !q) {
      var note = document.createElement("div");
      note.className = "card";
      note.id = "actual-partial";
      note.innerHTML = "<h3>仅有监测 / 订单口径的城市</h3><p class='board-desc'>以下城市未公布全市接待人次，以监测口径或平台订单量替代，不参与上方排序。</p>" +
        D.cities_2025_partial.map(function (p) {
          return "<div class='kv'><span class='k'>" + esc(p.city) + "（" + esc(p.province) + "）</span><span>" + esc(p.note) + "</span></div>";
        }).join("");
      main.appendChild(note);
    }
  }

  function renderPredict() {
    var main = el("main");
    var q = state.q;
    main.innerHTML = "";

    // 参考榜单（按平台分列，避免一眼全是地名）
    var ref = document.createElement("div");
    ref.className = "card";
    ref.id = "predict-ref";
    ref.innerHTML = "<h3>2026 预订 / 热度信号（参考榜单）</h3><p class='board-desc'>今年国庆哪些城市可能人流量高——多平台预订数据，按平台分列。</p>";
    ref.appendChild(subSection("✈️ 机票预订 TOP10", D.rankings.flight.meta.source, chips(D.rankings.flight.list, null, 10)));
    ref.appendChild(subSection("🏨 同程 · 提前订 TOP10", "同程旅行", chips(D.rankings.hotel_tongcheng.list, null, 10)));
    ref.appendChild(subSection("🏨 去哪儿 · 酒店抢订 TOP10", "去哪儿旅行", chips(D.rankings.hotel_qunar.list, null, 10)));
    ref.appendChild(subSection("🗺️ 长线游热门省份", "平台综合", chips(D.rankings.longhaul.list, null, 5)));
    main.appendChild(ref);

    // 城市综合热度
    var cities = D.cities.filter(function (c) { return hit(q, c.city + c.province); })
      .sort(function (a, b) { return b.heat_score - a.heat_score; });
    var cols = [
      { key: "city", label: "城市", fmt: function (r) { return esc(r.city); } },
      { key: "province", label: "省份", fmt: function (r) { return esc(r.province); } },
      { key: "heat_score", label: "综合热度", num: true, fmt: function (r) { return "<b>" + fmt(r.heat_score, 1) + "</b>"; } },
      { key: "visits_wan", label: "去年接待(万)", num: true, fmt: function (r) { return r.has_2025 ? fmt(r.visits_wan, 0) : "—"; } },
      { key: "flight_rank", label: "机票榜", fmt: function (r) { return rankBadge(r.flight_rank); } },
      { key: "hotel_tongcheng_rank", label: "提前订榜", fmt: function (r) { return rankBadge(r.hotel_tongcheng_rank); } },
      { key: "hotel_qunar_rank", label: "酒店抢订", fmt: function (r) { return rankBadge(r.hotel_qunar_rank); } },
      { key: "pressure_level", label: "机票紧张", fmt: function (r) { return pBadge(r.pressure_level); } }
    ];
    main.appendChild(card(
      "城市综合热度榜（2026 预测）",
      "综合 = 去年基数 + 今年机票/酒店榜单位次 + 长线省份 + 机票紧张度。点击行看评分拆解。",
      table("predict", cols, cities, openCity),
      "多平台预订数据加权", "predict-heat"
    ));
  }

  function renderTicket() {
    var main = el("main");
    var q = state.q;
    main.innerHTML = "";

    // 全国信号
    var sig = document.createElement("div");
    sig.className = "card";
    sig.id = "ticket-sig";
    sig.innerHTML = "<h3>2026 全国出行信号</h3><div class='chips'>" +
      D.national_2026.map(function (n) {
        return "<span class='chip'><b>" + esc(n.metric) + "</b>：" + esc(n.value) +
          " <span class='rk'>" + esc(n.yoy) + "｜" + esc(n.source) + "</span></span>";
      }).join("") + "</div>";
    main.appendChild(sig);

    // 机票预订最热（紧张代理）
    var flightBox = document.createElement("div");
    flightBox.className = "card";
    flightBox.id = "ticket-flight";
    flightBox.innerHTML = "<h3>机票预订最热城市 TOP10（2026）</h3><p class='board-desc'>预订量越高，高峰日机票越容易被抢光——这是「卖得差不多了」的主要代理信号（非实时售罄）。</p>";
    var flightRows = D.rankings.flight.list.map(function (name, i) {
      var rec = D.cities.filter(function (c) { return c.city === name; })[0];
      return { rank: i + 1, city: name, province: rec ? rec.province : "—", flight_rank: i + 1 };
    });
    var fCols = [
      { key: "rank", label: "排名", num: true, fmt: function (r) { return "<b>" + r.rank + "</b>"; } },
      { key: "city", label: "城市", fmt: function (r) { return esc(r.city); } },
      { key: "province", label: "省份", fmt: function (r) { return esc(r.province); } },
      { key: "flight_rank", label: "机票热门位次", fmt: function (r) { return rankBadge(r.flight_rank); } }
    ];
    flightBox.appendChild(table("ticket-flight", fCols, flightRows, openCity));
    var fsrc = document.createElement("div");
    fsrc.className = "src";
    fsrc.textContent = "来源：" + D.rankings.flight.meta.source + "（" + D.rankings.flight.meta.as_of + "）｜" + D.rankings.flight.meta.note;
    flightBox.appendChild(fsrc);
    main.appendChild(flightBox);

    // 城市机票紧张度
    var cityP = D.cities.filter(function (c) {
      return c.pressure_level && hit(q, c.city + c.province);
    }).sort(function (a, b) { return b.pressure_score - a.pressure_score; });
    var pCols = [
      { key: "city", label: "城市", fmt: function (r) { return esc(r.city); } },
      { key: "province", label: "省份", fmt: function (r) { return esc(r.province); } },
      { key: "pressure_level", label: "等级", fmt: function (r) { return pBadge(r.pressure_level); } },
      { key: "pressure_score", label: "紧张分", num: true, fmt: function (r) { return fmt(r.pressure_score, 0); } },
      { key: "_detail", label: "说明", fmt: function (r) {
        var it = (r.pressure_items || [])[0];
        return it ? esc(it.detail) : "—";
      } }
    ];
    main.appendChild(card(
      "城市机票紧张度（今年国庆）",
      "哪些城市机票已卖得差不多了——按公开报道的紧张等级排序，点击行看完整证据。",
      table("ticket-city", pCols, cityP, openCity),
      "航旅纵横 / 航司售票部门 / 广西机场集团", "ticket-city"
    ));

    // 航线增幅
    var routeBox = document.createElement("div");
    routeBox.className = "card";
    routeBox.id = "ticket-route";
    routeBox.innerHTML = "<h3>长线 / 赏秋航线增幅（2026）</h3><p class='board-desc'>对角线赏秋与长航线预订暴涨，进藏、新疆、延吉等小机场尤为紧张。</p>";
    var rCols = [
      { key: "route", label: "航线 / 城市", fmt: function (r) { return esc(r.route); } },
      { key: "growth", label: "增幅", fmt: function (r) { return "<b>" + esc(r.growth) + "</b>"; } },
      { key: "km", label: "距离(km)", fmt: function (r) { return esc(r.km); } },
      { key: "tag", label: "标签", fmt: function (r) { return '<span class="pill">' + esc(r.tag) + "</span>"; } },
      { key: "source", label: "来源", fmt: function (r) { return esc(r.source); } }
    ];
    var routes = D.routes.filter(function (r) { return hit(q, r.route + r.tag); });
    routeBox.appendChild(table("ticket-route", rCols, routes));
    main.appendChild(routeBox);

    // 售罄 / 紧张清单
    var pressBox = document.createElement("div");
    pressBox.className = "card";
    pressBox.id = "ticket-press";
    pressBox.innerHTML = "<h3>机票紧张 / 低价清单（公开报道级证据）</h3><p class='board-desc'>国内整体仍有低价窗口；南宁等枢纽出发的高峰日（9/30-10/1、10/6-10/7）票价偏高、折扣票少。</p>";
    var pCols2 = [
      { key: "scope", label: "范围", fmt: function (r) { return esc(r.scope); } },
      { key: "level", label: "等级", fmt: function (r) { return pBadge(r.level); } },
      { key: "detail", label: "详情", fmt: function (r) { return esc(r.detail); } },
      { key: "as_of", label: "截至", fmt: function (r) { return esc(r.as_of); } },
      { key: "source", label: "来源", fmt: function (r) { return esc(r.source); } }
    ];
    var press = D.pressure.filter(function (r) { return hit(q, r.scope + r.detail); });
    pressBox.appendChild(table("ticket-press", pCols2, press));
    main.appendChild(pressBox);
  }

  function renderCounty() {
    var main = el("main");
    var q = state.q;
    main.innerHTML = "";

    var ref = document.createElement("div");
    ref.className = "card";
    ref.id = "county-ref";
    ref.innerHTML = "<h3>县域目的地参考榜单（2026）</h3><p class='board-desc'>「奔县反向游」成黑马——年轻人避开人挤人，转向县域小城，按平台分列。</p>";
    ref.appendChild(subSection("🏨 同程 · 县域 TOP10", "同程旅行", chips(D.rankings.county_tongcheng.list, null, 10)));
    ref.appendChild(subSection("🏨 去哪儿 · 县域 TOP10", "去哪儿旅行", chips(D.rankings.county_qunar.list, null, 10)));
    main.appendChild(ref);

    // 县域综合
    var counties = D.counties.filter(function (c) { return hit(q, c.name); });
    var cCols = [
      { key: "name", label: "县域", fmt: function (r) { return esc(r.name); } },
      { key: "tongcheng_rank", label: "同程榜", fmt: function (r) { return rankBadge(r.tongcheng_rank); } },
      { key: "qunar_rank", label: "去哪儿榜", fmt: function (r) { return rankBadge(r.qunar_rank); } },
      { key: "both", label: "双榜", fmt: function (r) { return r.both ? '<span class="badge normal">双榜</span>' : "—"; } },
      { key: "score", label: "热度分", num: true, fmt: function (r) { return "<b>" + fmt(r.score, 1) + "</b>"; } }
    ];
    main.appendChild(card(
      "县域目的地热度榜（2026）",
      "合并同程与去哪儿两个榜单，双榜同时上榜额外加权。",
      table("county", cCols, counties),
      "同程旅行 / 去哪儿旅行", "county-heat"
    ));

    // 城市黑马
    var dark = D.cities.filter(function (c) { return hit(q, c.city + c.province); })
      .sort(function (a, b) { return b.dark_score - a.dark_score; }).slice(0, 15);
    var dCols = [
      { key: "city", label: "城市", fmt: function (r) { return esc(r.city); } },
      { key: "province", label: "省份", fmt: function (r) { return esc(r.province); } },
      { key: "dark_score", label: "黑马分", num: true, fmt: function (r) { return "<b>" + fmt(r.dark_score, 1) + "</b>"; } },
      { key: "visits_wan", label: "去年接待(万)", num: true, fmt: function (r) { return r.has_2025 ? fmt(r.visits_wan, 0) : "—"; } },
      { key: "flight_rank", label: "机票榜", fmt: function (r) { return rankBadge(r.flight_rank); } },
      { key: "hotel_tongcheng_rank", label: "提前订榜", fmt: function (r) { return rankBadge(r.hotel_tongcheng_rank); } }
    ];
    main.appendChild(card(
      "城市黑马榜（低基数 + 高增速）",
      "黑马分 = 低接待基数 + 航线增幅 + 榜单位次；去年基数越小、今年涨势越猛越「黑」。",
      table("dark", dCols, dark, openCity),
      "综合推算", "county-dark"
    ));
  }

  /* ---------------- 城市详情 ---------------- */
  function openCity(row) {
    var c = row;
    var body = el("modalBody");
    var html = "<h2>" + esc(c.city) + "</h2><div class='prov'>" + esc(c.province) +
      (c.has_2025 ? " ｜ 2025 全市接待 " + fmt(c.visits_wan, 0) + " 万人次" : " ｜ 暂无 2025 全市口径") + "</div>";

    if (c.has_2025) {
      html += "<div class='detail-section'><h4>2025 国庆实际</h4><div class='stat-grid'>" +
        "<div class='stat'><div class='k'>接待人次</div><div class='v'>" + fmt(c.visits_wan, 0) + " <small>万</small></div></div>" +
        "<div class='stat'><div class='k'>同比</div><div class='v'>" + (c.visits_yoy == null ? "—" : yoy(c.visits_yoy)) + "</div></div>" +
        "<div class='stat'><div class='k'>旅游收入</div><div class='v'>" + fmt(c.revenue_yi, 1) + " <small>亿</small></div></div>" +
        "<div class='stat'><div class='k'>人均消费</div><div class='v'>" + fmt(c.per_capita, 0) + " <small>元</small></div></div>" +
        "</div>";
      html += "<div class='kv'><span class='k'>统计口径</span><span>" + esc(c.scope || "—") + "</span></div>";
      html += "<div class='kv'><span class='k'>数据来源</span><span>" + esc(c.source_2025 || "—") + "</span></div></div>";
    }

    html += "<div class='detail-section'><h4>2026 预订信号</h4>" +
      "<div class='kv'><span class='k'>机票热门榜</span><span>" + rankBadge(c.flight_rank) + "</span></div>" +
      "<div class='kv'><span class='k'>酒店提前订榜（同程）</span><span>" + rankBadge(c.hotel_tongcheng_rank) + "</span></div>" +
      "<div class='kv'><span class='k'>酒店抢订榜（去哪儿）</span><span>" + rankBadge(c.hotel_qunar_rank) + "</span></div>" +
      "<div class='kv'><span class='k'>长线游省份</span><span>" + (c.longhaul_province ? '<span class="badge normal">是</span>' : "否") + "</span></div>" +
      (c.partial_note ? "<div class='kv'><span class='k'>2025 备注</span><span>" + esc(c.partial_note) + "</span></div>" : "") +
      "</div>";

    html += "<div class='detail-section'><h4>综合热度分 " + (c.heat_score == null ? "—" : fmt(c.heat_score, 1)) + "</h4>";
    var parts = c.heat_parts || {};
    Object.keys(parts).forEach(function (k) {
      var v = parts[k];
      var pct = Math.max(2, Math.min(100, (v / 60) * 100));
      html += "<div class='kv'><span class='k'>" + esc(k) + "</span><span>" + fmt(v, 1) + "</span></div><div class='bar'><i style='width:" + pct + "%'></i></div>";
    });
    html += "</div>";

    if (c.pressure_level) {
      html += "<div class='detail-section'><h4>机票紧张度 " + pBadge(c.pressure_level) + "</h4>";
      (c.pressure_items || []).forEach(function (it) {
        html += "<div class='kv'><span class='k'>" + esc(it.scope) + "</span><span>" + pBadge(it.level) + "</span></div>" +
          "<div class='kv'><span class='k'>详情</span><span>" + esc(it.detail) + "</span></div>" +
          "<div class='kv'><span class='k'>截至 / 来源</span><span>" + esc(it.as_of || "—") + " ｜ " + esc(it.source || "—") + "</span></div>";
      });
      html += "</div>";
    }

    body.innerHTML = html;
    el("modal").hidden = false;
  }

  function closeModal() { el("modal").hidden = true; }

  /* ---------------- 渲染调度 ---------------- */
  var SECTIONS = {
    actual: [["actual-city", "城市接待量 Top"], ["actual-prov", "省份接待量 Top"], ["actual-partial", "监测/订单口径城市"]],
    predict: [["predict-ref", "预订热度信号(多平台)"], ["predict-heat", "城市综合热度榜"]],
    ticket: [["ticket-sig", "全国出行信号"], ["ticket-flight", "机票预订最热 TOP10"], ["ticket-city", "城市机票紧张度"], ["ticket-route", "长线/赏秋航线增幅"], ["ticket-press", "机票紧张/低价清单"]],
    county: [["county-ref", "县域参考榜单"], ["county-heat", "县域热度榜"], ["county-dark", "城市黑马榜"]]
  };

  function buildToc(tab) {
    var box = el("toc");
    if (!box) return;
    var list = (SECTIONS[tab] || []).filter(function (s) { return el(s[0]); });
    box.innerHTML = "<span class='toc-label'>本页榜单：</span>" + list.map(function (s) {
      return "<button type='button' class='toc-item' data-target='" + s[0] + "'>" + esc(s[1]) + "</button>";
    }).join("");
    box.querySelectorAll(".toc-item").forEach(function (b) {
      b.addEventListener("click", function () {
        var t = el(b.getAttribute("data-target"));
        if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  function render() {
    if (state.tab === "actual") renderActual();
    else if (state.tab === "predict") renderPredict();
    else if (state.tab === "ticket") renderTicket();
    else if (state.tab === "county") renderCounty();
    buildToc(state.tab);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  /* ---------------- 事件 ---------------- */
  document.getElementById("tabs").addEventListener("click", function (e) {
    var btn = e.target.closest(".tab");
    if (!btn) return;
    document.querySelectorAll(".tab").forEach(function (t) { t.classList.remove("active"); });
    btn.classList.add("active");
    state.tab = btn.getAttribute("data-tab");
    render();
  });
  var searchInput = el("search");
  searchInput.addEventListener("input", function () { state.q = searchInput.value.trim(); render(); });
  el("clearBtn").addEventListener("click", function () { searchInput.value = ""; state.q = ""; render(); searchInput.focus(); });
  el("modalClose").addEventListener("click", closeModal);
  el("modal").addEventListener("click", function (e) { if (e.target === el("modal")) closeModal(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });

  /* 回到顶部按钮 */
  var toTop = el("toTop");
  if (toTop) {
    toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
    window.addEventListener("scroll", function () {
      if (window.scrollY > 400) toTop.classList.add("show"); else toTop.classList.remove("show");
    }, { passive: true });
  }

  render();
})();
