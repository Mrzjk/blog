# 博客与社交系统 (Blog System)

这是一个基于 Vue 3（前端）和 FastAPI（后端）构建的现代化全栈博客与社交平台。项目采用了深色科技风格的 UI 设计，集成了实时聊天、系统通知、活跃度等级系统以及完善的博客文章管理与后台控制功能。

[English Documentation](README.md)

## 🚀 核心功能 (Features)

*   **现代化的 UI/UX 设计**：深色科技风主题，采用毛玻璃（Glassmorphism）特效、响应式布局及平滑的过渡动画。
*   **用户认证与安全**：基于 JWT 的安全用户注册、登录及状态管理。
*   **等级与经验系统 (Level & EXP)**：用户在线活跃即可自动获取经验升级，全站（文章流、评论区、聊天列表、个人主页）沉浸式展示专属用户等级徽章（`Lv.X`）。
*   **博客管理系统**：
    *   支持 Markdown 语法的富文本编辑器。
    *   文章分类与标签系统。
    *   文章互动：浏览量统计、点赞功能以及支持多层级嵌套（平铺展示）的评论系统，评论区全量显示用户等级并支持一键跳转主页。
    *   个人主页：展示用户个人信息、当前经验条进度及支持分页的“我的文章”列表。
*   **实时社交系统（类 QQ 聊天体验）**：
    *   基于 WebSockets 的低延迟实时通信。
    *   好友系统：搜索用户、发送好友请求、同意或拒绝请求。
    *   类 QQ 聊天布局：左侧全局好友列表（附带在线状态与等级显示），右侧独立聊天窗口。
    *   **单方消息控制**：支持单方面清空聊天记录、删除会话或删除单条消息，且绝不会影响对方的历史记录。
*   **后台管理面板 (Admin Dashboard)**：
    *   数据仪表盘，实时统计总用户数、文章数及待审核动态。
    *   系统设置持久化：可随时开启/关闭全局注册、发文是否需要强制人工审核等开关。
    *   用户管理：管理员可封禁/禁言用户、重置密码、分配角色以及**手动修改用户经验值并自动同步等级**。
    *   全局公告：一键向全站所有用户下发系统通知。
*   **通知中心**：集中管理好友请求、文章点赞及评论通知，支持已读/未读状态切换及分页展示。

## 🛠️ 技术栈 (Technology Stack)

### 前端 (Frontend)
*   **框架**: Vue 3 (Composition API, `<script setup>`)
*   **构建工具**: Vite
*   **状态管理**: Pinia
*   **路由**: Vue Router
*   **UI 组件库**: Element Plus
*   **样式方案**: Tailwind CSS + 自定义 CSS 变量
*   **网络请求**: Axios, 原生 WebSockets

### 后端 (Backend)
*   **框架**: FastAPI (Python)
*   **数据库**: SQLite (通过 SQLAlchemy ORM 进行操作)
*   **认证与加密**: Passlib (Bcrypt), python-jose, JWT
*   **实时通信**: FastAPI WebSockets

## 📂 目录结构 (Project Structure)

```text
blog/
├── frontend/             # Vue 3 前端应用
│   ├── src/
│   │   ├── api/          # API 接口集成
│   │   ├── components/   # 可复用的 Vue 组件
│   │   ├── layouts/      # 布局组件 (包含后台与前台独立布局)
│   │   ├── router/       # Vue Router 路由配置
│   │   ├── store/        # Pinia 状态管理 (user, chat)
│   │   ├── utils/        # 工具函数 (如 request.js 拦截器)
│   │   └── views/        # 页面视图 (主页、聊天、后台管理、文章详情等)
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── backend/              # FastAPI 后端应用
    ├── app/
    │   ├── api/          # API 路由端点 (认证、文章、聊天、后台控制等)
    │   ├── core/         # 核心配置 (安全配置、环境变量)
    │   ├── models/       # SQLAlchemy 数据库模型
    │   ├── schemas/      # Pydantic 数据验证模型
    │   └── main.py       # FastAPI 应用入口文件
    ├── seed.py           # 数据库初始化/测试数据填充脚本
    └── requirements.txt  # Python 依赖清单
```

## 🏁 快速启动 (Getting Started)

### 环境要求 (Prerequisites)
*   Docker & Docker Compose (推荐)
*   或者 Node.js (v16+) 和 Python (v3.8+) 用于本地开发

### 🐳 使用 Docker 快速部署 (推荐)

使用 Docker 是一键启动本项目的最快方式。

1.  克隆项目：
    ```bash
    git clone <repository-url>
    cd blog
    ```
2.  构建并启动容器：
    ```bash
    docker-compose up -d --build
    ```
3.  访问应用：
    *   前端页面: `http://localhost`
    *   后端 API 文档: `http://localhost:8001/docs`

*注：后端首次运行时会自动在容器内生成一个本地的 SQLite 数据库 (`blog_social.db`)*。

### 💻 本地开发环境搭建

如果你想分别运行前后端进行二次开发：

#### 后端服务启动 (Backend Setup)

1.  进入后端目录：
    ```bash
    cd backend
    ```
2.  安装 Python 依赖：
    ```bash
    pip install -r requirements.txt
    ```
3.  初始化数据库并生成测试数据（可选，但强烈建议执行以获取丰富的展示效果）：
    ```bash
    python seed.py
    ```
4.  启动 FastAPI 服务器（默认运行在 8001 端口）：
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    ```
    *启动成功后，可以访问 `http://127.0.0.1:8001/docs` 查看由 Swagger UI 自动生成的 API 文档。*

### 前端服务启动 (Frontend Setup)

1.  进入前端目录：
    ```bash
    cd frontend
    ```
2.  安装 Node 依赖：
    ```bash
    npm install
    ```
3.  启动开发服务器：
    ```bash
    npm run dev
    ```
    *前端服务通常会运行在 `http://localhost:5173` 或 `http://localhost:5174`，请留意控制台输出。*

## 📝 配置说明 (Configuration)

请确保前端正确指向了后端 API 的地址。
如果后端端口发生改变，请检查 `frontend/vite.config.ts` 中的代理配置，或 `frontend/src/utils/request.ts` 中的 `baseURL`，确保其与您的 FastAPI 服务端口保持一致。