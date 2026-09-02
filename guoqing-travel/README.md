# 国庆旅游热度榜 · 查询工具

一个纯静态的单页应用，用于在 Vercel 上展示：

- **去年人气（2025）**：去年国庆哪些城市人流量最高（各地文旅局实际接待量）。
- **今年预测（2026）**：今年国庆哪些城市可能人流量高（机票 / 酒店预订与平台热度加权）。
- **机票紧张度（2026）**：哪些城市国庆机票已卖得差不多了（含售罄清单、航线增幅）。
- **县域 / 黑马（2026）**：反向游走红的县域与小基数高增速城市。

顶部搜索框可跨榜单查询城市 / 省份；点击任意城市行查看完整详情。

## 目录结构

```
guoqing-travel/
├── index.html      # 页面结构
├── styles.css      # 样式
├── app.js          # 查询 / 排序 / 榜单渲染逻辑
├── data.js         # 数据（由 travel_data.py 生成，勿手改）
├── gen_data.py     # 数据重新生成脚本
├── vercel.json     # Vercel 静态托管配置
└── README.md
```

数据源头在仓库根目录的 `travel_data.py`（`data_snapshot()` 导出完整 JSON）。

## 本地预览

在 `guoqing-travel` 目录下执行：

```bash
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

## 更新数据

修改根目录 `../travel_data.py` 后，重新生成 `data.js`：

```bash
python gen_data.py
```

## 部署到 Vercel

本目录是独立的可部署单元（只含静态文件）。三种方式任选其一：

### 方式一：Vercel CLI（推荐）

```bash
# 在 guoqing-travel 目录下
npx vercel          # 首次，按提示登录并部署
npx vercel --prod   # 推到生产域名
```

### 方式二：导入 Git 仓库并指定根目录

1. Vercel 控制台 → New Project → 导入本仓库。
2. **Root Directory** 设为 `guoqing-travel`（关键，避免误用根目录的充电宝项目）。
3. Framework 选 `Other` / 不构建，直接 Deploy。

### 方式三：Deploy 按钮

在仓库 README 中加：

```markdown
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/你的用户名/你的仓库&root-directory=guoqing-travel)
```

## 数据说明

数据来自各地文旅局、携程、去哪儿、同程旅行、美团旅行、航旅纵横、中国旅游报等公开报道整理，**非实时余票接口**。2025 年为各地实际接待口径（统计范围不完全一致，跨城比较仅供参考）；2026 年为预订 / 搜索热度信号。机票余票请以航司与售票平台实时查询为准。
