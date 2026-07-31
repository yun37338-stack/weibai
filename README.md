# 味白 · 个人工作台

> 记账 · 计划 · 随笔 — 你的数字生活管家

「味白」是一站式个人工作台应用。部署一次，手机电脑都能用，**每个设备数据独立隔离**。

---

## 各平台使用指南

---

### 📱 手机端（推荐：Render 一键云端部署）

> 部署一次，得到一个公网链接，手机直接打开就能用。**不需要电脑一直开着。**

#### 第一步：一键部署

点击下方按钮，用 GitHub 账号登录 Render（免费）：

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yun37338-stack/weibai)

等待 2-3 分钟，部署完成后你会得到一个链接，类似：

```
https://weibai-xxxx.onrender.com
```

#### 第二步：手机安装

**Android 手机（Chrome 浏览器）**：

1. 打开 Chrome，访问上面的链接
2. 底部会自动弹出 **"添加到主屏幕"** 提示
3. 点击 **"添加"** → 桌面出现「味白」图标
4. 如果没有弹出提示：点右上角 `⋮` → 添加到主屏幕

**iPhone 手机（Safari 浏览器）**：

1. 打开 Safari，访问上面的链接
2. 点底部中间 **分享按钮**（方框+箭头图标）
3. 向下滑动，找到 **"添加到主屏幕"**
4. 点右上角 **"添加"** → 桌面出现「味白」图标

#### 安装后的体验

- 桌面图标打开 → 全屏运行，和原生 App 一模一样
- 首次打开后，基础页面支持**离线访问**（没有网络也能打开）
- **数据隔离**：每个设备自动生成唯一 ID，A 和 B 的数据完全互不可见

> 如果需要更新到最新版：Render 后台点击 "Manual Deploy" → "Clear build cache & deploy" 即可。

---

### 💻 电脑端（本地运行）

**Windows 用户（最简单）**：

1. [下载代码 ZIP](https://github.com/yun37338-stack/weibai/archive/refs/heads/main.zip) 并解压
2. 双击 `启动味白.bat` → 自动安装依赖并启动
3. 浏览器自动打开 `http://localhost:8000`

**Mac / Linux 用户**：

```bash
# 1. 下载代码
git clone https://github.com/yun37338-stack/weibai.git
cd weibai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python app.py

# 4. 浏览器打开 http://localhost:8000
```

**电脑启动后，手机也能连**：

1. 确保手机和电脑连同一 WiFi
2. 查看电脑 IP 地址：
   - Windows：CMD 输入 `ipconfig`，找"IPv4 地址"
   - Mac：终端输入 `ifconfig | grep inet`，找 `192.168.x.x`
3. 手机浏览器访问 `http://<电脑IP>:8000` → 添加到主屏幕

> 这种方式的优点是：手机和电脑共享同一份数据，数据都在你的电脑上。

---

## 功能介绍

### 🏠 欢迎页（首页）
- 每日不重复的夸夸语录（365+句）
- 每日一句（联网 Hitokoto API，离线兜底）
- 今日收支概览
- 实时微博热搜（点击跳转查看）
- 今日计划、本周计划、长期计划预览（可直接打勾）

### 💰 记账
- **快速记账**：支出 / 收入双模式，分类按钮一键选择
- **分类分离**：支出分类（餐饮/交通/购物/娱乐/住房/医疗/教育/其他）与收入分类（工资/生活费/兼职/理财/红包/报销/其他）独立管理
- **自定义分类**：可添加删除分类，支持上传自定义图标（PNG/JPG）
- **补录历史**：支持选择任意日期补录账单
- **编辑 / 删除**：每笔账单可修改金额/分类/备注/类型，或直接删除
- **总账视图**：
  - 图表概览模式：饼图（支出分类占比）、柱状图（每日收支）、折线图（收支趋势）、树状图（分类矩形热力图）
  - 账单详情模式：日历网格展示当月每天收支，点击任意日期展开账单明细（含删除按钮）
  - 全年模式：12月月度卡片，点击跳转到具体月份日历
- **年度总账**：同样支持图表概览（折线图/柱状图/月结余/饼图）和月度明细切换

### ✅ 计划
- **今日计划**：打勾/取消、添加、编辑（自定义弹窗）、删除
- **周计划**：支持设置开始和结束日期，显示时间区间
- **长期计划**：无截止日期的长期目标管理
- 首页三栏预览：今日 / 本周 / 长期，可直接打勾

### ✍️ 随笔
- 每日随笔编辑（自动保存当天唯一一篇）
- 历史随笔按日期列表查看
- 支持修改已写随笔

### ⚙️ 设置
- **用户称呼**：自定义欢迎页的称呼（默认：主人）
- **主题色**：6种预设（海绿/岩灰/暖棕/苔青/墨蓝/藕紫），实时切换
- **应用图标**：可上传自定义图标替换默认🌿
- **记账分类管理**：支出分类 + 收入分类两栏独立管理，支持添加/删除/上传图标

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python FastAPI + uvicorn |
| 数据库 | SQLite（`data.db`，自动建表） |
| 前端 | 原生 HTML/CSS/JS（SPA 单页应用） |
| 图表 | Canvas 原生绘制（饼图/柱状图/折线图/树状图） |
| 图标 | SVG（Heroicons 风格） |
| 字体 | Noto Sans SC + Noto Serif SC（Google Fonts） |
| PWA | Service Worker + manifest.json（可安装到手机桌面） |
| 热搜 | 微博官方接口 `weibo.com/ajax/side/hotSearch` |
| 每日一句 | Hitokoto.cn API |

---

## API 接口一览

### 设置
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/settings` | 获取全部设置（用户名/主题/图标/自定义分类） |
| PUT | `/api/settings` | 更新设置 |
| GET | `/api/settings/cat-icons` | 获取分类图标 |
| POST | `/api/settings/cat-icon/upload` | 上传分类图标 |
| POST | `/api/settings/upload-icon` | 上传应用图标 |

### 仪表盘
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard` | 首页聚合数据（今日收支、计划、随笔、热点等） |

### 每日内容
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/today/quote` | 每日一句 |
| GET | `/api/today/compliment` | 夸夸语录（每天不重复） |
| GET | `/api/today/hot` | 微博实时热搜 |

### 计划
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/plans?plan_date=&plan_type=` | 获取计划列表 |
| POST | `/api/plans/add` | 添加计划 |
| PUT | `/api/plans/{id}` | 编辑计划内容 |
| PUT | `/api/plans/{id}/toggle` | 切换完成状态 |
| DELETE | `/api/plans/{id}` | 删除计划 |

### 随笔
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/essays/today` | 获取今日随笔 |
| GET | `/api/essays` | 获取所有随笔 |
| POST | `/api/essays/add` | 添加随笔 |
| PUT | `/api/essays/{id}` | 编辑随笔 |

### 记账
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bills?month=&date=` | 获取账单列表 |
| POST | `/api/bills/add` | 添加账单（含 `bill_date` 补录） |
| PUT | `/api/bills/{id}` | 编辑账单 |
| DELETE | `/api/bills/{id}` | 删除账单 |
| GET | `/api/bills/summary?year=&month=` | 总账/年度汇总（天级/月级+图表数据） |

---

## 项目结构

```
weibai/
├── app.py                  # FastAPI 主程序（31个API端点）
├── database.py             # SQLite 数据库层（建表/CRUD/联网数据）
├── data.db                 # SQLite 数据库文件（自动生成）
├── requirements.txt        # Python 依赖
├── static/
│   ├── index.html          # 前端 SPA（~1200行，含所有页面逻辑）
│   ├── manifest.json       # PWA 配置
│   ├── sw.js               # Service Worker（离线缓存）
│   ├── favicon.png         # 网站图标
│   ├── icon-192.png        # PWA 小图标
│   ├── icon-512.png        # PWA 大图标
│   └── uploads/            # 用户上传的图片
├── .gitignore
└── README.md
```

---

## Git 版本历史

| 提交 | 说明 |
|------|------|
| `c1c1eae` | 初始版：味白个人工作台 |
| `bae890f` | 账单记账优化：日历视图/图表切换/树状图/PWA |
| `5283385` | 记账收入优化：收支分类分离 |
| `2acd8ad` | 设备隔离：每设备独立数据 + 云端一键部署

---

## 许可证

MIT — 自由使用、修改、分发。
