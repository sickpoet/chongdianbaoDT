"""2026 中秋国庆旅游热度数据集。

数据口径说明
------------
- 2025 年数据为「实际接待」，假期为 2025-10-01 ~ 10-08（国庆中秋连休 8 天）。
- 2026 年数据为「预订 / 搜索热度」，假期为 2026-09-25 ~ 10-07
  （中秋 9/25-27 + 国庆 10/1-7，中间请 3 天年假可连休 13 天）。
- 每条数据尽量带 source 与 as_of；未披露的字段留 None，页面显示「—」，不做猜测填充。
- 没有免费的实时余票 API，机票紧张度只能来自公开报道，分四级：
  sold_out（已售罄）> tight（紧张·无折扣）> normal（正常）> cheap（价格低位）。
"""

from __future__ import annotations

META = {
    "updated": "2026-09-02",
    "holiday_2025": "2025-10-01 ~ 2025-10-08（国庆中秋连休 8 天）",
    "holiday_2026": "2026-09-25 ~ 2026-10-07（中秋 9/25-27 + 国庆 10/1-7）",
    "disclaimer": (
        "本站数据为公开报道与平台榜单的整理汇总，非实时接口。"
        "2025 年为各地文旅局公布的假期实际接待口径，不同城市统计范围（全市 / A 级景区 / 重点监测）"
        "并不完全一致，跨城比较仅供参考。机票余票请以航司和售票平台实时查询为准。"
    ),
}

# ---------------------------------------------------------------------------
# 一、2025 年（去年）实际客流 —— 城市级
# visits_wan: 接待人次（万）；revenue_yi: 旅游收入（亿元）；per_capita: 人均消费（元）
# scope: 统计口径；source: 来源
# ---------------------------------------------------------------------------
CITIES_2025: list[dict] = [
    {"city": "成都", "province": "四川", "visits_wan": 2862.30, "visits_yoy": 5.30, "revenue_yi": 293.50, "revenue_yoy": 13.40, "per_capita": 1025.40, "scope": "全市", "source": "成都市文旅局"},
    {"city": "重庆", "province": "重庆", "visits_wan": 2701.59, "visits_yoy": 4.20, "revenue_yi": 196.14, "revenue_yoy": 11.40, "per_capita": 726.02, "scope": "全市（国内游客）", "source": "重庆市文旅委"},
    {"city": "上海", "province": "上海", "visits_wan": 2548.50, "visits_yoy": 19.74, "revenue_yi": None, "revenue_yoy": None, "per_capita": None, "scope": "全市", "source": "上海市文化和旅游局"},
    {"city": "北京", "province": "北京", "visits_wan": 2509.40, "visits_yoy": 3.60, "revenue_yi": 316.50, "revenue_yoy": 4.70, "per_capita": 1261.26, "scope": "全市", "source": "北京市文旅局"},
    {"city": "杭州", "province": "浙江", "visits_wan": 2264.16, "visits_yoy": 10.50, "revenue_yi": 193.10, "revenue_yoy": 4.50, "per_capita": 852.85, "scope": "全市", "source": "杭州市文化广电旅游局"},
    {"city": "天津", "province": "天津", "visits_wan": 2219.59, "visits_yoy": 5.70, "revenue_yi": 215.75, "revenue_yoy": 13.20, "per_capita": 972.03, "scope": "全市", "source": "天津市文化和旅游局"},
    {"city": "南京", "province": "江苏", "visits_wan": 2009.70, "visits_yoy": 30.20, "revenue_yi": 279.40, "revenue_yoy": 34.80, "per_capita": 1390.26, "scope": "全市", "source": "南京市文旅局 / 银联商务"},
    {"city": "西安", "province": "陕西", "visits_wan": 2007.75, "visits_yoy": 28.00, "revenue_yi": 199.59, "revenue_yoy": 38.70, "per_capita": 994.10, "scope": "全市", "source": "西安市文化和旅游局"},
    {"city": "苏州", "province": "江苏", "visits_wan": 2000.00, "visits_yoy": 15.30, "revenue_yi": None, "revenue_yoy": None, "per_capita": None, "scope": "全市（近 2000 万）", "source": "苏州市文化广电和旅游局"},
    {"city": "广州", "province": "广东", "visits_wan": 1738.00, "visits_yoy": 5.50, "revenue_yi": 156.50, "revenue_yoy": 18.10, "per_capita": 900.46, "scope": "全市", "source": "广州市文化广电旅游局"},
    {"city": "昆明", "province": "云南", "visits_wan": 1579.51, "visits_yoy": 8.75, "revenue_yi": 182.43, "revenue_yoy": 12.63, "per_capita": 1155.06, "scope": "全市（国内游客）", "source": "昆明市文化和旅游局"},
    {"city": "沈阳", "province": "辽宁", "visits_wan": 1560.26, "visits_yoy": 11.80, "revenue_yi": 140.94, "revenue_yoy": 12.50, "per_capita": 903.31, "scope": "全市（国内游客）", "source": "沈阳市文化旅游和广播电视局"},
    {"city": "宁波", "province": "浙江", "visits_wan": 1208.11, "visits_yoy": 9.62, "revenue_yi": 146.18, "revenue_yoy": 10.54, "per_capita": 1209.99, "scope": "全市", "source": "宁波市文化广电旅游局"},
    {"city": "哈尔滨", "province": "黑龙江", "visits_wan": 1080.70, "visits_yoy": 13.20, "revenue_yi": 72.41, "revenue_yoy": 12.30, "per_capita": 670.03, "scope": "全市", "source": "哈尔滨市文化广电和旅游局"},
    {"city": "长沙", "province": "湖南", "visits_wan": 1079.52, "visits_yoy": 13.39, "revenue_yi": 85.49, "revenue_yoy": 5.36, "per_capita": 791.93, "scope": "全市", "source": "长沙市文化旅游广电局"},
    {"city": "深圳", "province": "广东", "visits_wan": 920.26, "visits_yoy": 12.40, "revenue_yi": 89.40, "revenue_yoy": 17.60, "per_capita": 971.46, "scope": "全市", "source": "深圳市文化广电旅游体育局"},
    {"city": "湖州", "province": "浙江", "visits_wan": 911.10, "visits_yoy": 8.10, "revenue_yi": None, "revenue_yoy": None, "per_capita": None, "scope": "全市", "source": "湖州市文化广电旅游局"},
    {"city": "安阳", "province": "河南", "visits_wan": 858.44, "visits_yoy": None, "revenue_yi": 53.95, "revenue_yoy": None, "per_capita": 628.47, "scope": "全市", "source": "安阳市文化广电体育旅游局"},
    {"city": "南阳", "province": "河南", "visits_wan": 840.96, "visits_yoy": 1.27, "revenue_yi": 42.14, "revenue_yoy": 4.51, "per_capita": 501.09, "scope": "全市", "source": "南阳市文化广电和旅游局"},
    {"city": "开封", "province": "河南", "visits_wan": 783.76, "visits_yoy": None, "revenue_yi": 54.80, "revenue_yoy": None, "per_capita": 699.19, "scope": "全市", "source": "开封市文化广电和旅游局"},
    {"city": "许昌", "province": "河南", "visits_wan": 776.00, "visits_yoy": None, "revenue_yi": 52.80, "revenue_yoy": None, "per_capita": 680.41, "scope": "全市", "source": "许昌市文化广电和旅游局"},
    {"city": "兰州", "province": "甘肃", "visits_wan": 663.86, "visits_yoy": 10.90, "revenue_yi": 40.07, "revenue_yoy": 12.95, "per_capita": 603.59, "scope": "全市", "source": "兰州市文化和旅游局"},
    {"city": "金华", "province": "浙江", "visits_wan": 546.71, "visits_yoy": 13.27, "revenue_yi": None, "revenue_yoy": None, "per_capita": None, "scope": "全市", "source": "金华市文化广电旅游局"},
    {"city": "大理州", "province": "云南", "visits_wan": 521.61, "visits_yoy": None, "revenue_yi": 66.12, "revenue_yoy": None, "per_capita": 1267.61, "scope": "全州", "source": "大理州文化和旅游局"},
    {"city": "凉山州", "province": "四川", "visits_wan": 502.51, "visits_yoy": 21.56, "revenue_yi": 48.62, "revenue_yoy": 24.08, "per_capita": 967.54, "scope": "全州", "source": "凉山州文化广播电视和旅游局"},
    {"city": "南平", "province": "福建", "visits_wan": 502.34, "visits_yoy": None, "revenue_yi": 34.11, "revenue_yoy": None, "per_capita": 679.02, "scope": "全市", "source": "南平市文化和旅游局"},
    {"city": "温州", "province": "浙江", "visits_wan": 493.70, "visits_yoy": None, "revenue_yi": 65.20, "revenue_yoy": None, "per_capita": 1320.64, "scope": "全市", "source": "温州市文化广电旅游局"},
    {"city": "龙岩", "province": "福建", "visits_wan": 468.86, "visits_yoy": None, "revenue_yi": 31.26, "revenue_yoy": None, "per_capita": 666.72, "scope": "全市", "source": "龙岩市文化和旅游局"},
    {"city": "岳阳", "province": "湖南", "visits_wan": 438.10, "visits_yoy": 20.92, "revenue_yi": 50.55, "revenue_yoy": 30.76, "per_capita": 1153.85, "scope": "全市", "source": "岳阳市文化旅游广电局"},
    {"city": "三明", "province": "福建", "visits_wan": 355.63, "visits_yoy": None, "revenue_yi": 28.49, "revenue_yoy": None, "per_capita": 801.11, "scope": "全市", "source": "三明市文化和旅游局"},
    {"city": "三门峡", "province": "河南", "visits_wan": 338.31, "visits_yoy": 0.85, "revenue_yi": 10.88, "revenue_yoy": -0.82, "per_capita": 321.60, "scope": "全市", "source": "三门峡市文化广电和旅游局"},
    {"city": "益阳", "province": "湖南", "visits_wan": 324.19, "visits_yoy": 24.06, "revenue_yi": None, "revenue_yoy": None, "per_capita": None, "scope": "全市", "source": "益阳市文化旅游广电体育局"},
    {"city": "昌吉州", "province": "新疆", "visits_wan": 244.89, "visits_yoy": 8.70, "revenue_yi": 17.41, "revenue_yoy": 9.55, "per_capita": 710.93, "scope": "全州", "source": "昌吉州文化体育广播电视和旅游局"},
    {"city": "大庆", "province": "黑龙江", "visits_wan": 244.50, "visits_yoy": 14.90, "revenue_yi": None, "revenue_yoy": None, "per_capita": None, "scope": "全市", "source": "大庆市文化广电和旅游局"},
    {"city": "海口", "province": "海南", "visits_wan": 113.45, "visits_yoy": 0.38, "revenue_yi": 14.14, "revenue_yoy": 3.25, "per_capita": 1246.36, "scope": "全市", "source": "海口市旅游和文化广电体育局"},
    {"city": "延吉", "province": "吉林", "visits_wan": 105.00, "visits_yoy": None, "revenue_yi": 21.40, "revenue_yoy": None, "per_capita": 2038.10, "scope": "全市", "source": "延吉市文化广播电视和旅游局"},
]

# 只有监测口径（非全市）的城市，单独一类，避免和全市口径混排
CITIES_2025_PARTIAL: list[dict] = [
    {"city": "济南", "province": "山东", "note": "纳入监测的 30 家景区接待 403.47 万人次；持证留宿旅客 96.01 万人次", "source": "济南市文化和旅游局"},
    {"city": "大同", "province": "山西", "note": "8 家重点监测景区累计接待 152.04 万人次", "source": "大同市文化和旅游局"},
    {"city": "佛山", "province": "广东", "note": "全市过夜游客 105.45 万人次，同比增长 12.13%", "source": "佛山市文化广电旅游体育局"},
    {"city": "福州", "province": "福建", "note": "整体旅游订单量同比增长 35%，酒店订单金额同比增长 241%（携程口径，非接待人次）", "source": "携程 / 同程旅行"},
    {"city": "武汉", "province": "湖北", "note": "线下实体店消费 221.55 亿元；武汉江滩累计接待超 120 万人次（非全市接待人次）", "source": "武汉市商务局"},
    {"city": "贵阳", "province": "贵州", "note": "累计消费金额 113.17 亿元，同比增长 7.1%（银联商务口径）", "source": "银联商务 / 贵阳市商务局"},
    {"city": "青岛", "province": "山东", "note": "未公布全市接待人次；周杰伦演唱会带动酒店预订同比增长 20%（2026 年数据）", "source": "去哪儿旅行"},
]

# ---------------------------------------------------------------------------
# 二、2025 年（去年）实际客流 —— 省级
# ---------------------------------------------------------------------------
PROVINCES_2025: list[dict] = [
    {"province": "河南", "visits_wan": 8136.30, "visits_yoy": 89.10, "revenue_yi": 539.10, "revenue_yoy": 83.40, "per_capita": 662.59},
    {"province": "河北", "visits_wan": 7484.61, "visits_yoy": 14.80, "revenue_yi": 578.86, "revenue_yoy": 14.40, "per_capita": 773.40},
    {"province": "辽宁", "visits_wan": 6579.42, "visits_yoy": 17.54, "revenue_yi": 443.84, "revenue_yoy": 18.20, "per_capita": 674.59},
    {"province": "广东", "visits_wan": 6517.60, "visits_yoy": 11.50, "revenue_yi": 613.20, "revenue_yoy": 14.20, "per_capita": 940.84},
    {"province": "江苏", "visits_wan": 6075.15, "visits_yoy": 24.48, "revenue_yi": 644.93, "revenue_yoy": 23.73, "per_capita": 1061.59},
    {"province": "陕西", "visits_wan": 5262.84, "visits_yoy": 14.37, "revenue_yi": 403.90, "revenue_yoy": 15.37, "per_capita": 767.46},
    {"province": "四川", "visits_wan": 4734.15, "visits_yoy": 8.32, "revenue_yi": 384.01, "revenue_yoy": 6.53, "per_capita": 811.15},
    {"province": "福建", "visits_wan": 4600.00, "visits_yoy": 14.50, "revenue_yi": 388.00, "revenue_yoy": 16.80, "per_capita": 843.48},
    {"province": "山西", "visits_wan": 4386.40, "visits_yoy": 5.16, "revenue_yi": 281.40, "revenue_yoy": 8.53, "per_capita": 641.53},
    {"province": "湖南", "visits_wan": 3992.94, "visits_yoy": 19.35, "revenue_yi": 502.06, "revenue_yoy": 25.96, "per_capita": 1257.37},
    {"province": "浙江", "visits_wan": 3760.30, "visits_yoy": 7.30, "revenue_yi": 546.80, "revenue_yoy": 8.80, "per_capita": 1454.14},
    {"province": "吉林", "visits_wan": 3473.00, "visits_yoy": None, "revenue_yi": 252.90, "revenue_yoy": None, "per_capita": 728.19},
    {"province": "重庆", "visits_wan": 2701.59, "visits_yoy": 4.20, "revenue_yi": 196.14, "revenue_yoy": 11.40, "per_capita": 726.02},
    {"province": "黑龙江", "visits_wan": 2612.50, "visits_yoy": 13.30, "revenue_yi": 111.20, "revenue_yoy": 15.00, "per_capita": 425.65},
    {"province": "上海", "visits_wan": 2548.50, "visits_yoy": 19.74, "revenue_yi": None, "revenue_yoy": None, "per_capita": None},
    {"province": "广西", "visits_wan": 2539.75, "visits_yoy": 22.64, "revenue_yi": 151.75, "revenue_yoy": 37.46, "per_capita": 597.50},
    {"province": "内蒙古", "visits_wan": 2531.20, "visits_yoy": 10.28, "revenue_yi": 176.86, "revenue_yoy": 9.77, "per_capita": 698.72},
    {"province": "北京", "visits_wan": 2509.40, "visits_yoy": 3.60, "revenue_yi": 316.50, "revenue_yoy": 4.70, "per_capita": 1261.26},
    {"province": "天津", "visits_wan": 2219.59, "visits_yoy": 5.70, "revenue_yi": 215.75, "revenue_yoy": 13.20, "per_capita": 972.03},
    {"province": "新疆", "visits_wan": 1863.84, "visits_yoy": 11.26, "revenue_yi": 250.96, "revenue_yoy": 11.71, "per_capita": 1346.47},
    {"province": "宁夏", "visits_wan": 683.10, "visits_yoy": 38.50, "revenue_yi": 49.70, "revenue_yoy": 30.40, "per_capita": 727.57},
    {"province": "海南", "visits_wan": 480.58, "visits_yoy": 1.70, "revenue_yi": 68.51, "revenue_yoy": 4.50, "per_capita": 1425.57},
    {"province": "西藏", "visits_wan": 375.52, "visits_yoy": None, "revenue_yi": 19.47, "revenue_yoy": None, "per_capita": 518.48},
    {"province": "青海", "visits_wan": 357.74, "visits_yoy": 13.92, "revenue_yi": 34.39, "revenue_yoy": 14.47, "per_capita": 961.31},
    {"province": "香港", "visits_wan": 139.40, "visits_yoy": None, "revenue_yi": 14.64, "revenue_yoy": None, "per_capita": None},
    {"province": "澳门", "visits_wan": 114.40, "visits_yoy": None, "revenue_yi": 1.90, "revenue_yoy": None, "per_capita": None},
]

# ---------------------------------------------------------------------------
# 三、2026 年（今年）预订 / 热度信号
# ---------------------------------------------------------------------------

# 国内机票预订热门目的地 TOP10（出行日 9/25-10/7，截至 8/11）
FLIGHT_TOP_2026: list[str] = ["北京", "上海", "广州", "成都", "深圳", "昆明", "乌鲁木齐", "重庆", "西安", "杭州"]
FLIGHT_TOP_2026_META = {
    "as_of": "2026-08-11",
    "source": "航旅纵横民航官方直销平台大数据",
    "note": "截至 8/11 国内航线机票预订量超 171 万张（同比 +7%）；截至 8/14 超 191 万张（同比 +7%）",
}

# 酒店抢订量 TOP10（截至 8 月下旬）
HOTEL_QUNAR_TOP_2026: list[str] = ["南京", "北京", "青岛", "上海", "成都", "深圳", "阿勒泰", "呼伦贝尔", "重庆", "济南"]
HOTEL_QUNAR_TOP_2026_META = {
    "as_of": "2026-08-26",
    "source": "去哪儿旅行",
    "note": "热门城市酒店提前预订量同比增长近四成；商圈前五均为演唱会场馆周边",
}

# 酒店「提前订」十大热门城市（截至 8/24）
HOTEL_TONGCHENG_TOP_2026: list[str] = ["成都", "广州", "上海", "西安", "北京", "青岛", "苏州", "南京", "三亚", "太原"]
HOTEL_TONGCHENG_TOP_2026_META = {
    "as_of": "2026-08-24",
    "source": "同程旅行",
    "note": "成都提前订热度月环比增长超 75%，居首",
}

# 国内长线跟团游 / 定制游预订热度前五省份
LONGHAUL_PROVINCES_2026: list[str] = ["新疆", "西藏", "甘肃", "云南", "海南"]
LONGHAUL_PROVINCES_2026_META = {
    "as_of": "2026-08-24",
    "source": "同程旅行",
    "note": "6-10 天产品占比超六成；1200 公里以上长航线机票预订热度月环比 +56%",
}

# 县域目的地 TOP10
COUNTY_TONGCHENG_2026: list[str] = ["安吉", "婺源", "建水", "黟县", "平遥", "昭苏", "阳朔", "荔波", "平潭", "仙居"]
COUNTY_TONGCHENG_2026_META = {
    "as_of": "2026-08-24",
    "source": "同程旅行",
    "note": "县域产品预订热度月环比 +60%；县域租车提前订热度月环比涨幅接近 80%",
}

COUNTY_QUNAR_2026: list[str] = ["布尔津", "九寨沟", "阳朔", "哈巴河", "新源", "安图", "平潭", "德钦", "婺源", "抚松"]
COUNTY_QUNAR_2026_META = {
    "as_of": "2026-08-11",
    "source": "去哪儿旅行",
    "note": "预订最火热的县城前十名",
}

# 航线预订量同比增幅（赏秋 / 长线）
ROUTE_SURGE_2026: list[dict] = [
    {"route": "拉萨 → 上海", "growth": "4.4 倍", "km": "约 2960", "tag": "对角线赏秋", "source": "去哪儿旅行"},
    {"route": "拉萨 → 北京", "growth": "3.4 倍", "km": "约 2640", "tag": "对角线赏秋", "source": "去哪儿旅行"},
    {"route": "拉萨 → 广州", "growth": "3.3 倍", "km": "约 2760", "tag": "对角线赏秋", "source": "去哪儿旅行"},
    {"route": "西宁 → 上海", "growth": "2.8 倍", "km": "约 1880", "tag": "对角线赏秋", "source": "去哪儿旅行"},
    {"route": "乌鲁木齐 → 南京", "growth": "约 2 倍", "km": "约 3040", "tag": "对角线赏秋", "source": "去哪儿旅行"},
    {"route": "乌鲁木齐 → 武汉", "growth": "约 2 倍", "km": "约 2760", "tag": "对角线赏秋", "source": "去哪儿旅行"},
    {"route": "飞往乌鲁木齐 / 伊犁", "growth": "月环比 +72%", "km": "—", "tag": "长航线", "source": "同程旅行"},
    {"route": "飞往迪庆 / 德宏", "growth": "月环比 +63%", "km": "—", "tag": "长航线", "source": "同程旅行"},
    {"route": "延吉（小机场增幅第一）", "growth": "3.8 倍", "km": "—", "tag": "小机场黑马", "source": "去哪儿旅行"},
    {"route": "中卫（宁夏）", "growth": "接近翻倍", "km": "—", "tag": "小机场黑马", "source": "去哪儿旅行"},
    {"route": "阿勒泰（新疆）", "growth": "接近翻倍", "km": "—", "tag": "小机场黑马", "source": "去哪儿旅行"},
]
ROUTE_SURGE_2026_META = {"as_of": "2026-08-26", "source": "去哪儿旅行 / 同程旅行"}

# ---------------------------------------------------------------------------
# 四、机票紧张度（公开报道级证据，非实时接口）
# level: sold_out > tight > normal > cheap
# ---------------------------------------------------------------------------
TICKET_PRESSURE_2026: list[dict] = [
    {
        "scope": "南宁 → 东盟（新加坡 / 吉隆坡 / 曼谷 / 雅加达 / 金边 / 万象 / 仰光 / 胡志明市）",
        "level": "sold_out",
        "detail": "国庆期间往返机票已基本售罄",
        "as_of": "2026-08-22",
        "source": "广西机场管理集团 / 广西民航售票部门",
        "cities": ["南宁"],
    },
    {
        "scope": "南宁 → 台北",
        "level": "tight",
        "detail": "往返折扣机票难觅踪影",
        "as_of": "2026-08-22",
        "source": "广西民航售票部门",
        "cities": ["南宁"],
    },
    {
        "scope": "南宁 → 昆明 / 海口 / 深圳 / 珠海 / 杭州 / 汕头 / 长沙 / 重庆 / 成都 / 南昌 / 合肥 / 福州 / 厦门 / 郑州 / 银川 / 乌鲁木齐",
        "level": "tight",
        "detail": "9/30-10/1、10/6-10/7 两个出行高峰期间票价较高，大多已无折扣机票",
        "as_of": "2026-08-22",
        "source": "广西民航售票部门",
        "cities": ["南宁"],
    },
    {
        "scope": "南宁 → 北京 / 上海",
        "level": "normal",
        "detail": "10 月 1 日部分航班仍有 5 折机票销售（运力安排充沛）",
        "as_of": "2026-08-22",
        "source": "广西民航售票部门",
        "cities": ["南宁"],
    },
    {
        "scope": "南宁 → 香港 / 澳门",
        "level": "cheap",
        "detail": "往返程目前还可以买到折扣机票",
        "as_of": "2026-08-22",
        "source": "广西民航售票部门",
        "cities": ["南宁"],
    },
    {
        "scope": "欧洲长线（团队游产品，非裸票）",
        "level": "sold_out",
        "detail": "春秋集团：欧洲全线产品基本售罄，售罄节奏远快于 2025 年",
        "as_of": "2026-08-27",
        "source": "春秋集团 / 央视网",
        "cities": [],
    },
    {
        "scope": "免签长线（土耳其 / 埃及 / 摩洛哥 / 南非 / 肯尼亚 / 塞尔维亚 / 俄罗斯）",
        "level": "sold_out",
        "detail": "收客量环比激增约 300%，部分热门线路提前两个月售罄",
        "as_of": "2026-08-26",
        "source": "众信旅游 / 广之旅",
        "cities": [],
    },
    {
        "scope": "国内航线整体（9/27 - 10/1 出发）",
        "level": "cheap",
        "detail": "机票均价创近三年同期最低；旅游产品价格较 2025 年同期下降约 5%",
        "as_of": "2026-08-26",
        "source": "去哪儿旅行 / 广之旅",
        "cities": [],
    },
    {
        "scope": "国内航线整体（截至 8/14）",
        "level": "normal",
        "detail": "国内机票预订量超 191 万张（同比 +7%）；出入境 135 万张（同比 +11%）",
        "as_of": "2026-08-14",
        "source": "航旅纵横",
        "cities": [],
    },
    {
        "scope": "中秋首日（9/25）部分航线",
        "level": "cheap",
        "detail": "北京 → 上海 / 杭州 / 西安，广州 → 杭州 / 武汉等多条航线有 2 折机票在售",
        "as_of": "2026-08-14",
        "source": "航旅纵横",
        "cities": ["北京", "上海", "广州", "杭州", "西安", "武汉"],
    },
]

PRESSURE_LEVELS = {
    "sold_out": {"label": "已售罄", "color": "#dc2626", "bg": "#fef2f2", "score": 10},
    "tight": {"label": "紧张·无折扣", "color": "#ea580c", "bg": "#fff7ed", "score": 7},
    "normal": {"label": "正常", "color": "#2563eb", "bg": "#eff6ff", "score": 4},
    "cheap": {"label": "价格低位", "color": "#16a34a", "bg": "#f0fdf4", "score": 2},
}

# ---------------------------------------------------------------------------
# 五、2026 年全国总量信号
# ---------------------------------------------------------------------------
NATIONAL_2026: list[dict] = [
    {"metric": "国内航线机票预订量", "value": "超 191 万张", "yoy": "同比 +7%", "as_of": "截至 2026-08-14", "source": "航旅纵横"},
    {"metric": "出入境航线机票预订量", "value": "超 135 万张", "yoy": "同比 +11%", "as_of": "截至 2026-08-14", "source": "航旅纵横"},
    {"metric": "出发机票搜索热度", "value": "同比增长 61%", "yoy": "8 月以来", "as_of": "2026-08", "source": "去哪儿旅行"},
    {"metric": "出境游搜索热度", "value": "同比增长 72%", "yoy": "8 月以来", "as_of": "2026-08", "source": "多家平台综合"},
    {"metric": "全国铁路预计发送旅客", "value": "2.19 亿人次", "yoy": "运输期 9/29 - 10/10 共 12 天", "as_of": "2026 年国庆中秋运输方案", "source": "国铁集团"},
    {"metric": "日均出入境旅客", "value": "175 万人次", "yoy": "同比 +18.5%", "as_of": "国家移民管理局预测", "source": "国家移民管理局"},
    {"metric": "9/27 - 10/1 机票均价", "value": "近三年同期最低", "yoy": "—", "as_of": "2026-08-26", "source": "去哪儿旅行"},
    {"metric": "拼假（9/28-30）酒店预订", "value": "同比增长 52%", "yoy": "每 7 个长假订单至少 1 个来自请假", "as_of": "2026-08-26", "source": "去哪儿旅行"},
]

# 出行高峰日
PEAK_DAYS_2026: list[dict] = [
    {"date": "9/24 - 9/26", "desc": "拼假大军首波高峰，全年溢价最重", "level": "high"},
    {"date": "9/25", "desc": "中秋节当日，首个出行峰值", "level": "high"},
    {"date": "9/28 - 9/30", "desc": "拼假错峰窗口，性价比较高", "level": "mid"},
    {"date": "10/1", "desc": "国庆节当日，第二个人流顶峰", "level": "high"},
    {"date": "10/3 - 10/5", "desc": "假期中段，票价回落 15%-20%", "level": "low"},
    {"date": "10/6 - 10/7", "desc": "返程最高峰，票价高、延误率高", "level": "high"},
    {"date": "10/8 之后", "desc": "票价逐渐回落", "level": "low"},
]

# ---------------------------------------------------------------------------
# 六、查询索引：把 2026 信号挂到城市上
# ---------------------------------------------------------------------------

def _rank_of(name: str, ranking: list[str]) -> int | None:
    try:
        return ranking.index(name) + 1
    except ValueError:
        return None


def _pressure_for_city(city: str) -> list[dict]:
    """只返回明确点名该城市的条目；cities 为空的全局 / 宏观条目不挂靠到单个城市。"""
    out = []
    for item in TICKET_PRESSURE_2026:
        cities = item.get("cities") or []
        if not cities:
            continue  # 全局 / 宏观条目（如欧洲长线、国内整体）属于大盘信号，不逐个城市归因
        if city not in cities:
            continue
        out.append(item)
    return out


def _pressure_score(city: str) -> tuple[int, str | None]:
    """返回（紧张度得分，最高等级 key）。没有针对该城市的证据时返回 (0, None)。"""
    items = _pressure_for_city(city)
    if not items:
        return 0, None
    best = None
    for it in items:
        lv = it["level"]
        if best is None or PRESSURE_LEVELS[lv]["score"] > PRESSURE_LEVELS[best]["score"]:
            best = lv
    return PRESSURE_LEVELS[best]["score"], best


# 长线省份热度权重（按同程 TOP5 顺序递减）
_LONGHAUL_WEIGHT = {"新疆": 10, "西藏": 9, "甘肃": 8, "云南": 7, "海南": 6}

# 航线增幅映射到城市（用于黑马分）
_ROUTE_CITY_BOOST = {
    "拉萨": 25, "西宁": 18, "乌鲁木齐": 16, "伊犁": 12, "延吉": 25,
    "中卫": 14, "阿勒泰": 16, "迪庆": 12, "德宏": 12,
}


def build_city_index() -> list[dict]:
    """把 2025 实况、2026 信号、紧张度合并成一份城市索引。"""
    max_visits = max((c["visits_wan"] for c in CITIES_2025), default=1.0)
    index: dict[str, dict] = {}

    for c in CITIES_2025:
        city = c["city"]
        flight_rank = _rank_of(city, FLIGHT_TOP_2026)
        hotel_q_rank = _rank_of(city, HOTEL_QUNAR_TOP_2026)
        hotel_t_rank = _rank_of(city, HOTEL_TONGCHENG_TOP_2026)
        p_score, p_level = _pressure_score(city)

        # 绝对热度：去年基数 + 今年榜单位次
        base_score = 30.0 * (c["visits_wan"] / max_visits)
        flight_score = 20.0 * (11 - flight_rank) / 10 if flight_rank else 0.0
        q_score = 15.0 * (11 - hotel_q_rank) / 10 if hotel_q_rank else 0.0
        t_score = 15.0 * (11 - hotel_t_rank) / 10 if hotel_t_rank else 0.0
        longhaul_score = float(_LONGHAUL_WEIGHT.get(c["province"], 0))
        pressure_score = float(p_score)
        heat = base_score + flight_score + q_score + t_score + longhaul_score + pressure_score

        # 黑马分：基数越小越「黑」，只看增速与位次信号
        dark_base = 15.0 * (1 - c["visits_wan"] / max_visits)
        dark_route = float(_ROUTE_CITY_BOOST.get(city, 0))
        dark_list = (q_score / 15 * 25) + (t_score / 15 * 15)
        dark_county = 0.0
        dark_heat = dark_base + dark_route + dark_list + dark_county

        index[city] = {
            "city": city,
            "province": c["province"],
            "has_2025": True,
            "visits_wan": c["visits_wan"],
            "visits_yoy": c["visits_yoy"],
            "revenue_yi": c["revenue_yi"],
            "revenue_yoy": c["revenue_yoy"],
            "per_capita": c["per_capita"],
            "scope": c["scope"],
            "source_2025": c["source"],
            "flight_rank": flight_rank,
            "hotel_qunar_rank": hotel_q_rank,
            "hotel_tongcheng_rank": hotel_t_rank,
            "longhaul_province": c["province"] in _LONGHAUL_WEIGHT,
            "pressure_level": p_level,
            "pressure_score": p_score,
            "pressure_items": _pressure_for_city(city),
            "heat_score": round(heat, 1),
            "heat_parts": {
                "去年基数": round(base_score, 1),
                "机票榜": round(flight_score, 1),
                "酒店抢订榜": round(q_score, 1),
                "提前订榜": round(t_score, 1),
                "长线省份": round(longhaul_score, 1),
                "紧张度": round(pressure_score, 1),
            },
            "dark_score": round(dark_heat, 1),
            "dark_parts": {
                "低基数": round(dark_base, 1),
                "航线增幅": round(dark_route, 1),
                "榜单位次": round(dark_list, 1),
            },
        }

    # 只有监测口径（非全市）的城市：也加入索引，便于查询，但 has_2025=False 不进「去年人气」榜
    for c in CITIES_2025_PARTIAL:
        city = c["city"]
        if city in index:
            index[city]["partial_note"] = c.get("note")
            continue
        flight_rank = _rank_of(city, FLIGHT_TOP_2026)
        hotel_q_rank = _rank_of(city, HOTEL_QUNAR_TOP_2026)
        hotel_t_rank = _rank_of(city, HOTEL_TONGCHENG_TOP_2026)
        p_score, p_level = _pressure_score(city)
        flight_score = 20.0 * (11 - flight_rank) / 10 if flight_rank else 0.0
        q_score = 15.0 * (11 - hotel_q_rank) / 10 if hotel_q_rank else 0.0
        t_score = 15.0 * (11 - hotel_t_rank) / 10 if hotel_t_rank else 0.0
        longhaul_score = float(_LONGHAUL_WEIGHT.get(c["province"], 0))
        pressure_score = float(p_score)
        heat = 8.0 + flight_score + q_score + t_score + longhaul_score + pressure_score
        dark_route = float(_ROUTE_CITY_BOOST.get(city, 0))
        dark_heat = 15.0 + dark_route + (q_score / 15 * 25) + (t_score / 15 * 15)
        index[city] = {
            "city": city,
            "province": c["province"],
            "has_2025": False,
            "visits_wan": None,
            "visits_yoy": None,
            "revenue_yi": None,
            "revenue_yoy": None,
            "per_capita": None,
            "scope": None,
            "source_2025": c.get("source"),
            "partial_note": c.get("note"),
            "flight_rank": flight_rank,
            "hotel_qunar_rank": hotel_q_rank,
            "hotel_tongcheng_rank": hotel_t_rank,
            "longhaul_province": c["province"] in _LONGHAUL_WEIGHT,
            "pressure_level": p_level,
            "pressure_score": p_score,
            "pressure_items": _pressure_for_city(city),
            "heat_score": round(heat, 1),
            "heat_parts": {
                "去年基数": 8.0,
                "机票榜": round(flight_score, 1),
                "酒店抢订榜": round(q_score, 1),
                "提前订榜": round(t_score, 1),
                "长线省份": round(longhaul_score, 1),
                "紧张度": round(pressure_score, 1),
            },
            "dark_score": round(dark_heat, 1),
            "dark_parts": {
                "低基数": 15.0,
                "航线增幅": round(dark_route, 1),
                "榜单位次": round((q_score / 15 * 25) + (t_score / 15 * 15), 1),
            },
        }

    # 只有 2026 信号、没有 2025 全市口径数据的城市（阿勒泰、三亚、太原等）
    extra_names: list[tuple[str, str]] = []
    for name in HOTEL_QUNAR_TOP_2026 + HOTEL_TONGCHENG_TOP_2026 + FLIGHT_TOP_2026:
        if name in index:
            continue
        if name in ("阿勒泰",):
            extra_names.append((name, "新疆"))
        elif name in ("呼伦贝尔",):
            extra_names.append((name, "内蒙古"))
        elif name in ("三亚",):
            extra_names.append((name, "海南"))
        elif name in ("太原",):
            extra_names.append((name, "山西"))
        elif name in ("青岛",):
            extra_names.append((name, "山东"))

    # 南宁：无 2025 全市口径、也不在机票/酒店榜，但有明确的机票紧张度证据，单独补入
    if "南宁" not in index:
        extra_names.append(("南宁", "广西"))

    for city, province in extra_names:
        flight_rank = _rank_of(city, FLIGHT_TOP_2026)
        hotel_q_rank = _rank_of(city, HOTEL_QUNAR_TOP_2026)
        hotel_t_rank = _rank_of(city, HOTEL_TONGCHENG_TOP_2026)
        p_score, p_level = _pressure_score(city)
        flight_score = 20.0 * (11 - flight_rank) / 10 if flight_rank else 0.0
        q_score = 15.0 * (11 - hotel_q_rank) / 10 if hotel_q_rank else 0.0
        t_score = 15.0 * (11 - hotel_t_rank) / 10 if hotel_t_rank else 0.0
        longhaul_score = float(_LONGHAUL_WEIGHT.get(province, 0))
        pressure_score = float(p_score)
        heat = 8.0 + flight_score + q_score + t_score + longhaul_score + pressure_score
        dark_route = float(_ROUTE_CITY_BOOST.get(city, 0))
        dark_heat = 15.0 + dark_route + (q_score / 15 * 25) + (t_score / 15 * 15)
        index[city] = {
            "city": city,
            "province": province,
            "has_2025": False,
            "visits_wan": None,
            "visits_yoy": None,
            "revenue_yi": None,
            "revenue_yoy": None,
            "per_capita": None,
            "scope": None,
            "source_2025": None,
            "flight_rank": flight_rank,
            "hotel_qunar_rank": hotel_q_rank,
            "hotel_tongcheng_rank": hotel_t_rank,
            "longhaul_province": province in _LONGHAUL_WEIGHT,
            "pressure_level": p_level,
            "pressure_score": p_score,
            "pressure_items": _pressure_for_city(city),
            "heat_score": round(heat, 1),
            "heat_parts": {
                "去年基数": 8.0,
                "机票榜": round(flight_score, 1),
                "酒店抢订榜": round(q_score, 1),
                "提前订榜": round(t_score, 1),
                "长线省份": round(longhaul_score, 1),
                "紧张度": round(pressure_score, 1),
            },
            "dark_score": round(dark_heat, 1),
            "dark_parts": {
                "低基数": 15.0,
                "航线增幅": round(dark_route, 1),
                "榜单位次": round((q_score / 15 * 25) + (t_score / 15 * 15), 1),
            },
        }

    return list(index.values())


def city_index() -> list[dict]:
    return build_city_index()


def county_index() -> list[dict]:
    """县域目的地索引（合并同程与去哪儿两个榜）。"""
    merged: dict[str, dict] = {}
    for i, name in enumerate(COUNTY_TONGCHENG_2026, start=1):
        merged[name] = {"name": name, "tongcheng_rank": i, "qunar_rank": None}
    for i, name in enumerate(COUNTY_QUNAR_2026, start=1):
        if name in merged:
            merged[name]["qunar_rank"] = i
        else:
            merged[name] = {"name": name, "tongcheng_rank": None, "qunar_rank": i}
    rows = []
    for name, m in merged.items():
        tc = m["tongcheng_rank"]
        qn = m["qunar_rank"]
        score = 0.0
        if tc:
            score += 20.0 * (11 - tc) / 10
        if qn:
            score += 20.0 * (11 - qn) / 10
        if tc and qn:
            score += 15.0  # 双榜同时上榜额外加权
        rows.append({**m, "score": round(score, 1), "both": bool(tc and qn)})
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows


def data_snapshot() -> dict:
    """导出给前端用的完整 JSON。"""
    return {
        "meta": META,
        "cities": city_index(),
        "counties": county_index(),
        "provinces_2025": PROVINCES_2025,
        "cities_2025_partial": CITIES_2025_PARTIAL,
        "national_2026": NATIONAL_2026,
        "peak_days": PEAK_DAYS_2026,
        "routes": ROUTE_SURGE_2026,
        "pressure": TICKET_PRESSURE_2026,
        "rankings": {
            "flight": {"list": FLIGHT_TOP_2026, "meta": FLIGHT_TOP_2026_META},
            "hotel_qunar": {"list": HOTEL_QUNAR_TOP_2026, "meta": HOTEL_QUNAR_TOP_2026_META},
            "hotel_tongcheng": {"list": HOTEL_TONGCHENG_TOP_2026, "meta": HOTEL_TONGCHENG_TOP_2026_META},
            "county_tongcheng": {"list": COUNTY_TONGCHENG_2026, "meta": COUNTY_TONGCHENG_2026_META},
            "county_qunar": {"list": COUNTY_QUNAR_2026, "meta": COUNTY_QUNAR_2026_META},
            "longhaul": {"list": LONGHAUL_PROVINCES_2026, "meta": LONGHAUL_PROVINCES_2026_META},
        },
    }
