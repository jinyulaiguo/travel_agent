# AI Travel Agent (智能旅游规划助手)

这是一个基于 AI 的智能旅游规划助手，能够根据用户的意图自动生成包含航班、目的地建议、景点规划、酒店推荐、每日行程、市内交通及费用汇总的完整旅行方案。

## 项目架构

- **Backend**: Python 3.13 + FastAPI + SQLAlchemy + LangGraph + pgvector
- **Frontend**: React 19 + TypeScript + Vite + Zustand + Ant Design
- **Infrastructure**: PostgreSQL (pgvector) + Redis

---

## 快速启动

### 1. 环境准备

确保您的系统中已安装以下工具：
- [Docker & Docker Compose](https://www.docker.com/)
- [Python 3.13+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)
- [uv](https://github.com/astral-sh/uv) (推荐的 Python 包管理器)

### 2. 启动基础设施

在项目根目录下运行，启动数据库和 Redis：

```bash
docker-compose up -d
```

### 3. 后端启动 (Backend)

1. 进入后端目录：
   ```bash
   cd backend
   ```
2. 配置文件：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入您的 OpenAI/DeepSeek API Key 以及其他必要参数
   ```
3. 安装依赖并启动：
   ```bash
   uv sync
   uv run uvicorn app.main:app --reload --port 8000
   ```
   API 文档地址：[http://localhost:8000/docs](http://localhost:8000/docs)

### 4. 前端启动 (Frontend)

1. 进入前端目录：
   ```bash
   cd frontend
   ```
2. 安装依赖：
   ```bash
   npm install
   ```
3. 启动开发服务器：
   ```bash
   npm run dev
   ```
   访问地址：[http://localhost:5173](http://localhost:5173)

---

## 核心功能模块

- **L0 意图澄清**: 通过 LLM 自动解析用户自然语言需求。
- **L1 航班锚点**: 实时获取或 Mock 航班数据并锁定时间。
- **L2 目的地确认**: 基于时间窗口建议停留天数。
- **L3 景点规划**: 智能标签匹配与地理聚类算法。
- **L4 酒店推荐**: 围绕景点重心（Centroid）推荐住宿区域及酒店。
- **L5 每日行程**: 自动排程算法，处理营业时间与特殊约束。
- **L6 市内交通**: 智能规划每日地点间的接驳方式。
- **L8 费用汇总**: 自动折算汇率并提供多维度花费统计。

## 审计与状态

本项目已通过功能审计（[参考审计报告](file:///Users/zhouyi/.gemini/antigravity/brain/d9a83364-4f67-4dab-956b-8629d0dd260a/walkthrough.md)），核心环节均已跑通。
