# 个人工作台

> 记账 · 拍照美食 · 日记 · 待办 — 一站式个人工作台

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
python app.py
```

### 3. 打开浏览器
访问 **http://localhost:8000**

## 功能

- 💰 **记账** — 收入/支出管理，分类统计，月度报表
- 📸 **拍照美食** — 拍照记录每天吃了什么，美食时间线
- 📝 **日记本** — 图文日记，心情标记，按日期归档
- ✅ **待办本** — 待办清单，优先级管理，完成打卡
- 📱 **PWA** — 手机浏览器打开可安装到主屏幕，像原生 App

## 技术栈

- 后端：Python FastAPI + SQLite
- 前端：原生 HTML/CSS/JS（PWA）
- 部署：GitHub Actions 自动打包

## 手机端使用

1. 用手机浏览器打开 `http://你的电脑IP:8000`
2. 浏览器菜单 → "添加到主屏幕"
3. 即可像原生 App 一样使用

## 项目结构

```
├── app.py              # FastAPI 主程序
├── database.py         # SQLite 数据库操作
├── requirements.txt    # Python 依赖
├── static/
│   ├── index.html      # 前端页面（单页应用）
│   ├── manifest.json   # PWA 配置
│   ├── sw.js           # Service Worker（离线缓存）
│   └── uploads/        # 图片上传目录
└── .github/workflows/  # GitHub Actions 自动发布
```
