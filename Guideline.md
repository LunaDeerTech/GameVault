# 游戏私有云管理平台 (Python + Electron 版)

## 1. 技术栈选型

### 服务端 (Server)
*   **语言:** **Python 3.10+**
*   **Web 框架:** **FastAPI**
    *   *理由:* 现代、异步（AsyncIO）高性能，自动生成 Swagger 文档，非常适合写 REST API。
*   **数据库:** **SQLite** (配合 **SQLAlchemy** 或 **Tortoise-ORM**)。
    *   *理由:* Python 处理 SQLite 非常方便，无需额外部署数据库服务。
*   **元数据刮削:** **BeautifulSoup4** 或 **httpx** (配合 Steam/IGDB API)。
*   **后台任务:** **APScheduler** (用于定时任务) 或 **Celery** (如果任务非常繁重，但初期推荐 APScheduler 以降低复杂度)。
*   **文件处理:** Python 原生 `hashlib` 和 `os` 模块，性能足够处理大多数 IO 密集型任务。

### 客户端 (Client - Windows)
*   **壳:** **Electron**
    *   *理由:* 跨平台架构（虽然你只做 Windows，但未来迁移 Linux/Mac 很方便），UI 能力天花板高。
*   **前端框架:** **Vue 3** 或 **React**。
    *   *理由:* 组件化开发，状态管理方便。
*   **核心逻辑 (Node.js):** Electron 的主进程 (Main Process) 运行在 Node.js 环境下，可以使用 Node 的 `fs` (文件系统) 和 `crypto` (加密/哈希) 模块来处理文件下载和对比。
*   **下载工具:** **Got** 或 **Axios** (支持流式下载)。

---

## 2. 项目结构规划

建议采用前后端分离的结构。

```text
/gamevault-root
  ├── /server (Python FastAPI)
  │    ├── /app
  │    │    ├── /api            # 路由接口 (endpoints)
  │    │    ├── /core           # 核心配置
  │    │    ├── /crud           # 数据库增删改查
  │    │    ├── /models         # 数据库模型
  │    │    ├── /schemas        # Pydantic 数据校验模型
  │    │    ├── /services       # 业务逻辑 (Scanner, Scraper, Hashing)
  │    │    └── main.py         # 启动文件
  │    ├── /storage             # 游戏存储目录 (示例)
  │    └── requirements.txt
  │
  └── /client (Electron + Vue)
       ├── /src
       │    ├── /main           # Electron 主进程 (处理本地文件、下载逻辑)
       │    ├── /renderer       # 前端界面 (Vue 代码)
       │    └── /common         # 共享的类型或工具
       ├── package.json
       └── electron-builder.yml # 打包配置
```

---

## 3. 核心功能实现方案

### 功能 1: 服务端目录扫描与刮削 (Python 强项)
Python 写爬虫和文件扫描是强项。
*   **流程:**
    1.  用户在管理员界面配置游戏路径 （例如：`/games`）。
    2.  FastAPI 启动一个后台线程扫描该目录。
    3.  解析文件夹名称，例如 `The Witcher 3`。
    4.  使用 Python 请求 Steam API 或 IGDB API。
    5.  下载封面图片到 `/storage/static/images`，将游戏信息（GameID, SteamID, IGDBID, 描述, 开发商等）存入 SQLite。
    6.  **关键:** 同时为该游戏目录生成 `manifest.json`（文件指纹），记录每个文件的路径、大小、修改时间和哈希值。

### 功能 2: 增量更新 (Node.js 主进程处理)
这是整个系统最复杂的部分。由于 Electron 的渲染进程（UI）不适合做重型 IO 操作，这些逻辑必须放在 Electron 的**主进程 (Main Process)** 中执行。

*   **服务端 (Python):**
    *   监控游戏目录的变化，定期更新 `manifest.json`。
    *   提供接口 `GET /api/games/{id}/manifest-hash` 返回该游戏的 `manifest.json` 的哈希值（用于快速对比）。
    *   提供接口 `GET /api/games/{id}/manifest` 返回完整的 `manifest` 内容。

*   **客户端 (Electron Main Process):**
    *   **Step 1:** 获取服务端 manifest hash，如果和本地存储的 hash 一致，说明没有更新，直接跳过。
    *   **Step 2 (差异对比):** 将服务端的 `manifest` 内容和本地的 `manifest` 进行对比，找出新增、修改和删除的文件。
    *   **Step 3 (生成任务):** 根据差异，生成“下载/覆盖列表”和“删除列表”。
    *   **Step 4 (断点下载):** 使用 Node.js 的 `fs.createWriteStream` 和 HTTP 请求库。
        *   如果是大文件局部更新：使用 `Range: bytes=start-end` 请求特定块，然后用 `r+` 模式打开本地文件写入指定位置。

### 功能 3: 游戏存档同步
*   **Python 端:** 
    *   提供接口接收客户端上传的存档文件。
    *   保存存档的路径和游戏 ID 到数据库。
    *   支持保存若干个版本的存档（如每次上传都保存一个新版本）。
*   **Electron 端:**
    *   利用 Node.js 的 `child_process` 模块来启动游戏 (`.exe`)。
    *   当子进程退出时，触发存档同步逻辑。
    *   使用 Node.js 的 `archiver` 库将存档目录打包成 zip，上传给服务器。
    *   查询数据库获取存档列表，展示在 UI 上，允许用户下载或恢复某个版本。

### 功能 4: 多用户管理
*   **Python:** 使用 `FastAPI Users` 库或手动实现 JWT (JSON Web Tokens)。
*   **Electron:** 登录成功后将 JWT 存入 `electron-store` (本地持久化配置)，每次请求 API 时在 Header 带上 Token。

---

## 4. 开发路线图 (Roadmap)

### 第一阶段：基础原型 (MVP)
1.  **Server:** 用 FastAPI 搭建服务，实现“扫描指定文件夹并列出文件名”的接口。
2.  **Client:** 用 Electron + Vue 搭建壳子，实现“登录”和“获取游戏列表”的 UI。
3.  **Download:** 实现最简单的“点击下载”，直接拉取整个文件夹（不考虑增量、优化等，先跑通 HTTP 下载）。

### 第二阶段：完善元数据与展示
1.  **Server:** 接入 Steam API，根据文件夹名自动匹配下载封面图。
2.  **Client:** 制作精美的“海报墙”界面，点击进入详情页可以看到背景图和简介。
3.  **Client:** 优化下载界面，显示进度条和状态。
4.  **Client:** 实现用户登录注册，管理员面板。

### 第三阶段：攻克增量更新 (难点)
1.  **Server:** 为每个游戏生成 `manifest.json`（包含文件哈希）。
2.  **Download:** 下载功能优化： 断点续传、多线程下载等。
3.  **Client:** 本地游戏完整性校验、修复。

### 第四阶段：存档与高级功能
1.  **Client:** 实现“启动游戏”按钮。
2.  **Client:** 监控游戏进程结束，查找存档并压缩上传。
3.  **Server:** 用户权限控制（如下载限速、禁止特定用户上传、禁止用户访问某些游戏等）。

---

## 5. Python + Electron 方案的优缺点总结

| 维度         | 优势                                                     | 挑战                                                         |
| :----------- | :------------------------------------------------------- | :----------------------------------------------------------- |
| **开发速度** | **极快**。Python 库多，Electron 写界面像写网页一样简单。 | 需要掌握两套语言环境 (Python & JS/TS)。                      |
| **界面美观** | **极高**。CSS/HTML 可以做出任何你想要的动画和特效。      | Electron 内存占用相对较高 (起步 100MB+)。                    |
| **性能**     | Python 服务端性能足够；Node.js IO 性能优秀。             | Python 处理超高并发文件传输可能不如 Go，但在私有云场景下完全不是瓶颈。 |
| **生态**     | Python 爬虫无敌；Node.js 各种 npm 包极其丰富。           | 需要处理 Python 后端和 Node 前端的交互协议。                 |
