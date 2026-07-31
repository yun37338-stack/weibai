# 味白 · 个人工作台 — 产品需求文档

> 版本：v1.0（已实现版）
>
> 更新日期：2026-07-31

---

## 一、产品概述

**味白**（WeiBai）是一站式个人生活管理工具，集记账、计划、随笔于一体。以"每天认真记录、温柔对待自己"为理念，帮助用户管理日常财务、规划任务、记录所思所想。

---

## 二、目标平台

| 平台 | 实现方式 |
|------|---------|
| Windows 电脑 | 浏览器访问 `localhost:8000`（Python 启动） |
| macOS 电脑 | 同上 |
| Android 手机 | Chrome PWA（添加到主屏幕） |
| iOS 手机 | Safari PWA（添加到主屏幕） |

---

## 三、已实现功能

### 3.1 欢迎页

- 称呼用户为自定义名称（默认"主人"，可在设置中修改）
- 日期 + 星期显示
- 每日不重复的夸夸语录（365+句本地语料库，按日期哈希轮换）
- 每日一句（联网 Hitokoto API，失败时本地兜底）
- 今日收支概览卡片
- 实时微博热搜（联网 `weibo.com/ajax/side/hotSearch`，点击可跳转）
- 今日计划 / 本周计划 / 长期计划三栏预览，可直接打勾
- 6 种预设主题色（海绿/岩灰/暖棕/苔青/墨蓝/藕紫）

### 3.2 记账（核心模块）

#### 快速记账
- 支出 / 收入双模式切换
- Canvas 原生图表（饼图/柱状图/折线图/树状图）
- 分类按钮快速选择
- 支持补录历史日期账单
- 编辑：弹出 Modal 修改金额/分类/备注/类型
- 删除：今日记账列表和总账展开明细均可删除

#### 分类管理
- **支出默认分类**：餐饮、交通、购物、娱乐、住房、医疗、教育、其他
- **收入默认分类**：工资、生活费、兼职、理财、红包、报销、其他
- 支出和收入分类 **完全独立**，切换类型时分类自动切换
- 支持添加自定义分类 + 上传自定义图标
- 默认分类不可删除，自定义分类可删除

#### 总账视图
- 年 / 月选择器 + 全年模式
- **[图表概览] / [账单详情]** 药丸式滑动切换
- 图表：饼图（支出分类占比）、柱状图（每日收支对比）、折线图（收支趋势）、树状图（分类矩形面积图）
- 详情：日历网格视图，7列（日一二三四五六），每天显示收支金额
  - 今天有绿色边框高亮
  - 有支出的天日期变红，有收入变绿
  - 点击日期展开当日账单明细（含删除按钮）

#### 年度总账
- 年份选择器
- **[图表概览] / [月度明细]** 切换
- 图表：折线图（12月收支趋势）、柱状图（月度对比）、月结余正负柱状图、饼图（全年收支比例）
- 明细：12月月度卡片

### 3.3 计划

#### 三种计划类型
- **今日计划**：指定日期的当天计划
- **周计划**：自定义开始日期 → 结束日期
- **长期计划**：无截止日期

#### 操作
- 圆框打勾 / 取消
- 右上角 + 按钮快速添加
- 编辑：弹出 Modal，修改内容和日期区间
- 删除：确认后删除

### 3.4 随笔

- 每日一篇随笔（自动保存当天唯一一篇）
- 历史随笔按日期列表显示
- 可编辑当天或过往随笔

### 3.5 设置

- 自定义用户称呼
- 6种主题色实时切换
- 上传应用图标替换默认🌿
- 记账分类管理（支出/收入两栏独立）

### 3.6 PWA（手机安装）

- `manifest.json`：应用名称、图标、全屏模式、快捷入口
- Service Worker：API 网络优先 + 静态资源缓存优先 + 离线兜底
- 可安装到 Android/iOS 主屏幕，像原生 App 一样使用

---

## 四、技术架构

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | Python FastAPI | 异步高性能，31个API端点 |
| Web 服务器 | uvicorn | 轻量级 ASGI 服务器 |
| 数据库 | SQLite | 零配置，文件级存储（`data.db`） |
| 前端 | 原生 HTML/CSS/JS | SPA 单页应用，无框架依赖 |
| 图表 | Canvas API | 原生绘制，无第三方库 |
| 图标 | SVG（Heroicons 风格） | 内联矢量图标 |
| 字体 | Google Fonts（Noto Sans SC + Noto Serif SC）| 无衬线中文 + 衬线中文标题 |
| PWA | Service Worker + manifest | 离线缓存 + 主屏幕安装 |
| 热搜 | 微博官方接口 | 52条实时热搜 |
| 每日一句 | Hitokoto.cn | 开放 API |

---

## 五、API 设计

### 5.1 设置
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/settings` | 返回 `{user_name, theme_color, app_icon, custom_categories}` |
| PUT | `/api/settings` | 全文更新设置 |
| GET | `/api/settings/cat-icons` | 分类自定义图标列表 |
| POST | `/api/settings/cat-icon/upload` | 上传分类图标（Multipart） |
| POST | `/api/settings/upload-icon` | 上传应用图标 |

### 5.2 仪表盘
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/dashboard` | 聚合返回今日收支/计划/随笔/热点/每日一句/夸夸 |

### 5.3 计划（完整 CRUD）
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/plans?plan_date=&plan_type=` | 按日期、类型筛选 |
| POST | `/api/plans/add` | `{content, plan_date, plan_type, end_date}` |
| PUT | `/api/plans/{id}/toggle` | 切换完成状态 |
| PUT | `/api/plans/{id}` | `{content}` 编辑内容 |
| DELETE | `/api/plans/{id}` | 删除 |

### 5.4 随笔
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/essays/today` | 今日随笔（仅一篇） |
| GET | `/api/essays` | 全部历史随笔 |
| POST | `/api/essays/add` | `{content}` |
| PUT | `/api/essays/{id}` | `{content}` 编辑 |

### 5.5 记账（完整 CRUD）
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/bills?month=&date=` | 按月份或具体日期筛选 |
| POST | `/api/bills/add` | `{type, amount, category, note, bill_date}` |
| PUT | `/api/bills/{id}` | `{type, category, amount, note}` 编辑 |
| DELETE | `/api/bills/{id}` | 删除 |
| GET | `/api/bills/summary?year=&month=` | `{total_income, total_expense, days[], monthly[]}` |

### 5.6 每日内容
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/today/quote` | 每日一句（联网+兜底） |
| GET | `/api/today/compliment` | 夸夸语录 |
| GET | `/api/today/hot` | 微博实时热搜 |

---

## 六、数据库设计

### bills（记账）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| type | TEXT | expense / income |
| amount | REAL | 金额 |
| category | TEXT | 分类名称 |
| note | TEXT | 备注 |
| created_at | TEXT | 记账时间（支持补录） |

### plans（计划）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| content | TEXT | 内容 |
| plan_date | TEXT | 计划日期 |
| end_date | TEXT | 结束日期（周计划） |
| done | INTEGER | 0/1 |
| plan_type | TEXT | daily / weekly / longterm |

### essays（随笔）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| content | TEXT | 内容 |
| created_at | TEXT | 创建时间 |

### settings（设置）
| 字段 | 类型 | 说明 |
|------|------|------|
| key | TEXT PK | 键名 |
| value | TEXT | 值 |

---

## 七、待规划功能

以下功能已在规划中，尚未实现：

- [ ] **AI 智能记账**：自然语言输入/语音记账，自动解析金额分类
- [ ] **拍照食物记录**：拍照 + 关联记账记录
- [ ] **预算设置与预警**：月预算上限提醒
- [ ] **数据导出**：CSV/Excel 导出账单
- [ ] **多设备数据同步**：云端存储方案
- [ ] **微信小程序**：Taro 跨端适配
- [ ] **Docker 一键部署**：简化服务启动

---

## 八、Git 版本记录

| Commit | 说明 |
|--------|------|
| `c1c1eae` | 初始版：欢迎页/记账/计划/随笔/设置/PWA 基础框架 |
| `bae890f` | 账单记账优化：日历视图/图表切换(饼/柱/折/树)/PWA离线/周长期计划打勾 |
| `5283385` | 记账收入优化：收支分类完全分离/收入专属分类/旧数据智能迁移 |

---

> 文档版本：v1.0 | 与实际代码同步
