# 个人工作台（Personal Workstation）产品需求文档

> 代号暂定，正式名待定
>
> 主理人：你
>
> 创建日期：2026-07-31

---

## 一、产品愿景

打造一个**集记账、日记、待办、拍照记录于一体的个人生活工作台**，同时支持电脑端和手机端，数据云端同步，开源部署，可通过 GitHub 打包下载。

核心理念：**一个应用，管理生活的方方面面——财务、时间、记忆、任务。**

---

## 二、GitHub 同类项目调研

经过调研，目前 GitHub 上**没有单一项目能完全覆盖"记账 + 日记 + 待办 + AI 智能记账 + 拍照食物记录"** 的全部需求。大多数项目只专注单一领域。以下是可参考的优质项目：

### 2.1 记账类（最值得参考）

| 项目 | Stars | 技术栈 | 亮点 |
|------|-------|--------|------|
| [mayswind/ezbookkeeping](https://github.com/mayswind/ezbookkeeping) | 1.9K+ | Go + Vue + PWA | **强烈推荐参考**。内置 AI OCR 小票识别、LLM 交易分类、PWA 一键添加到手机主屏、自托管、支持 Docker 部署、带图片附件和位置标记。最接近你的需求。 |
| [actualbudget/actual](https://github.com/actualbudget/actual) | 26.7K+ | TypeScript + React | 本地优先的个人财务应用，YNAB 开源替代品，支持多设备同步和端到端加密。 |
| [TNT-Likely/BeeCount](https://github.com/TNT-Likely/BeeCount) | - | Flutter + Supabase | 跨平台（iOS/Android）记账应用，多账簿管理、云端同步、统计图表。 |

### 2.2 待办类

| 项目 | Stars | 技术栈 | 亮点 |
|------|-------|--------|------|
| [plumqm/Todolist-demo](https://github.com/plumqm/Todolist-demo) | - | Taro/uni-app + Electron | 跨平台四端（Web/移动端/微信小程序/Windows桌面挂件），实时同步。 |

### 2.3 日记类

| 项目 | Stars | 技术栈 | 亮点 |
|------|-------|--------|------|
| 小熊の日记 (BearDiary) | - | 微信小程序 | 日记撰写、图片预览、本地存储。 |
| [laurent22/joplin](https://github.com/laurent22/joplin) | 52.4K+ | TypeScript + RN | 全能笔记+待办，全平台支持，端到端加密同步。但功能过重，不适合直接改造。 |

### 2.4 调研结论

**推荐策略：基于 [ezBookkeeping](https://github.com/mayswind/ezbookkeeping) 进行二次开发**，原因：
- 已有 AI 智能记账能力（OCR 收据识别 + LLM 分类）
- 已有 PWA 支持（手机端可直接安装到主屏幕）
- 已有图片附件功能（可扩展为拍照食物记录）
- Go + Vue 技术栈成熟稳定，Docker 一键部署
- MIT 开源协议，可自由修改分发

然后在此基础上扩展：待办模块、日记模块、拍照食物记录、欢迎页「主理人」品牌化。

如果 ezBookkeeping 改造难度大，则采用 **方案 B：Taro 从零搭建**，一套代码编译到微信小程序 + H5 + 桌面端。

---

## 三、目标平台

| 平台 | 实现方式 |
|------|---------|
| Windows 电脑 | Taro H5 / PWA / Electron 桌面端 |
| macOS 电脑 | Taro H5 / PWA / Electron 桌面端 |
| iOS 手机 | PWA（添加到主屏幕）/ 微信小程序 |
| Android 手机 | PWA（添加到主屏幕）/ 微信小程序 |

数据通过后端 API 同步，部署到自托管服务器或云服务器。通过 GitHub Actions 自动打包发布 Release。

---

## 四、功能模块

### 4.1 欢迎页（Home Dashboard）

- 称呼用户为「主理人」
- 今日概览卡片：
  - 今日支出 / 收入
  - 今日待办数量
  - 最近一篇日记
  - 今日吃了什么（最新食物照片）
- 快捷入口：记账、拍照、写日记、添加待办
- 可自定义的主题色和问候语

### 4.2 AI 智能记账（核心模块）

#### 4.2.1 手动记账
- 金额、分类（支出/收入）、类别（餐饮/交通/购物/娱乐/住房/医疗/教育/其他）
- 备注、日期、标签
- 多账户支持（现金、银行卡、微信、支付宝）

#### 4.2.2 AI 智能记账
- **拍照识别小票**：拍摄购物小票，AI（OCR + LLM）自动提取金额、商家、类别、日期
- **语音记账**：说出"今天午饭花了 35 块"，AI 自动解析并记账
- **自然语言输入**：输入"刚才打车去公司 28 元"，AI 自动识别分类填表
- AI 交易自动分类建议

#### 4.2.3 统计与分析
- 月/年收支趋势图
- 分类占比饼图
- 预算设置与预警
- 收支对比报表

### 4.3 拍照食物记录（记账扩展）

- 拍照记录今天吃了什么
- 自动关联到记账模块（可选填金额）
- 食物照片时间线展示
- 可按日期浏览
- 配合 AI 识别食物类别（早餐/午餐/晚餐/零食）
- 相当于一个「今天吃了什么」的视觉日记

### 4.4 小日记本

- 图文日记编写（Markdown 编辑器）
- 支持插入图片、表情
- 按日期/月份归档
- 日记卡片瀑布流展示
- 搜索和标签过滤
- 心情标记（开心/难过/平静/兴奋...）
- 日记可关联当天的记账记录

### 4.5 待办本

- 快速添加待办事项
- 清单视图 / 分组视图
- 优先级标记（高/中/低）
- 截止日期和提醒
- 完成打卡动画
- 每日/每周/自定义清单
- 待办可与日记/记账关联

---

## 五、技术方案

### 5.1 推荐技术栈（方案对比）

| 层级 | 方案 A（推荐） | 方案 B |
|------|-------------|--------|
| 跨端前端 | Taro 3（React/Vue3） | uni-app |
| 桌面端 | Taro H5 / Electron 封装 | Electron |
| 后端 | Go（Gin）/ Node.js（Nest.js） | Node.js / Python |
| 数据库 | SQLite（轻量） / PostgreSQL | MySQL / Supabase |
| AI | 通义千问 / DeepSeek / OpenAI API | 百度 OCR + LLM |
| 存储 | 本地文件 / 阿里云 OSS | Supabase Storage |
| 同步 | REST API + WebSocket | Supabase Realtime |
| CI/CD | GitHub Actions 自动打包发布 | GitHub Actions |
| 部署 | Docker 一键部署 | Vercel / Railway |

### 5.2 推荐最终选型（方案 A）

```
前端：Taro 3 + React + TypeScript + NutUI/Taro UI
后端：Go (Gin) 或 Node.js (Nest.js)  
数据库：SQLite（单机轻量）/ PostgreSQL（云同步）
AI：DeepSeek API / 通义千问 API（成本低效果好）
容器化：Docker + docker-compose
发布：GitHub Actions 自动构建 → GitHub Releases / GitHub Pages
```

### 5.3 目录结构

```
personal-workstation/
├── client/                 # Taro 前端
│   ├── src/
│   │   ├── pages/
│   │   │   ├── home/       # 欢迎页（主理人）
│   │   │   ├── accounting/ # 记账模块
│   │   │   ├── food/       # 拍照食物
│   │   │   ├── diary/      # 日记本
│   │   │   └── todo/       # 待办本
│   │   ├── components/     # 通用组件
│   │   ├── services/       # API 请求
│   │   └── stores/         # 状态管理
│   └── config/
├── server/                 # 后端服务
│   ├── api/                # 接口层
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑
│   ├── ai/                 # AI 集成
│   └── config/
├── docker/
├── .github/workflows/      # GitHub Actions CI/CD
├── docker-compose.yml
└── README.md
```

---

## 六、GitHub 部署与发布流程

1. **代码托管**：GitHub 仓库 `personal-workstation`
2. **自动构建**：
   - 每次 push 到 main 分支触发 GitHub Actions
   - 自动编译 Taro 前端为 H5 / 微信小程序
   - 自动编译后端为二进制文件或 Docker 镜像
3. **自动发布**：
   - 打 Tag（如 `v1.0.0`）触发 Release 构建
   - 自动生成 Release 页面，包含：
     - H5 网页版（GitHub Pages）
     - Docker 镜像
     - 微信小程序代码包
     - Windows/macOS 桌面安装包（可选）
4. **下载方式**：用户可从 GitHub Releases 页面下载对应版本

---

## 七、开发路线图

### 第一阶段：MVP 核心（v0.1）
- [x] 项目初始化 + 仓库搭建
- [ ] 欢迎页（主理人面板）
- [ ] 手动记账（增删改查）
- [ ] 记账分类管理
- [ ] 基础待办功能
- [ ] 数据本地存储

### 第二阶段：AI 智能（v0.2）
- [ ] AI 智能记账（自然语言输入）
- [ ] 拍照 OCR 识别小票
- [ ] 记账统计分析图表
- [ ] 拍照食物记录

### 第三阶段：日记与扩展（v0.3）
- [ ] 日记本模块（图文编辑）
- [ ] 待办本增强（优先级/提醒）
- [ ] 食物时间线

### 第四阶段：跨端与发布（v1.0）
- [ ] PWA 支持（手机安装到主屏幕）
- [ ] 微信小程序适配
- [ ] GitHub Actions 自动打包发布
- [ ] Docker 一键部署
- [ ] 数据云端同步

---

## 八、可先 Fork 改造的开源项目

按推荐优先级排序：

1. **[mayswind/ezbookkeeping](https://github.com/mayswind/ezbookkeeping)** — 最推荐。已具备 AI 记账核心能力，在上面扩展日记、待办、食物记录、主理人欢迎页。

2. **[TNT-Likely/BeeCount](https://github.com/TNT-Likely/BeeCount)** — 如果偏好 Flutter 技术栈，移动端体验更好，但需要从零补日记和待办。

3. **[plumqm/Todolist-demo](https://github.com/plumqm/Todolist-demo)** — 跨端框架参考，四端实时同步的实现思路可借鉴。

---

## 九、下一步行动建议

1. **决定技术路线**：Fork ezBookkeeping 改造 vs Taro 从零搭建
2. **初始化 GitHub 仓库**，配置 CI/CD
3. **搭建项目脚手架**，跑通 Hello World
4. **先做欢迎页 + 记账** 作为第一个可用的 MVP
5. **逐步迭代** 添加日记、待办、AI 功能

---

> 文档版本：v0.1
> 下一步：确认技术路线后开始编码实现。
