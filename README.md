---
title: Perplexity AI MCP Server
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

## 源项目地址：
https://github.com/helallao/perplexity-ai

## 🚀 一键部署到 Hugging Face Space

[![Deploy to HF Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/deploy-to-spaces-lg.svg)](https://huggingface.co/new-space?template=qoomezhu/perplexity-ai)

点击上方按钮，然后在 Space Settings → Secrets 中配置：

| Secret | 说明 |
|--------|------|
| `MCP_TOKEN` | API 认证密钥 (如 `sk-xxxxx`) |
| `TOKEN_POOL_JSON` | Token 配置，格式: `{"tokens":[{"id":"u1","csrf_token":"xxx","session_token":"yyy"}]}` |

---

## 展示
ADMIN
<img width="1751" height="900" alt="image" src="https://github.com/user-attachments/assets/baa6d6e0-1752-42e6-9eda-29930f8b9947" />

OAI playground
![img_v3_02u3_eada7873-379e-42c1-bcbf-3c0466a66ffg](https://github.com/user-attachments/assets/29d75f8e-2058-4945-b486-d50b09f140a1)

MCP
<img width="1894" height="989" alt="image" src="https://github.com/user-attachments/assets/4a495432-8305-4820-8b4a-d7e54986ba45" />


## 更新记录
+ 2026-01-28：添加 Hugging Face Space Docker 一键部署支持
+ 2026-01-27：优化 Vercel 部署支持，添加 Token 保活 GitHub Actions
+ 2026-01-19：增加SKILL，`.claude/skills/perplexity-search`
+ 2026-01-16: 重构项目结构，增加oai 端点适配
+ 2026-01-13: 新增心跳检测功能，支持定时检测token健康状态并通过Telegram通知
+ 2026-01-03: webui控制
+ 2026-01-02：新增多token池支持，支持动态管理号池（列举/新增/删除）
+ 2026-01-02：MCP 响应现在包含 `sources` 字段，返回搜索结果的来源链接
+ 2025-12-31：增加健康检查endpoint， http://127.0.0.1:8000/health

## 启动服务


## docker compose 一键部署

### 1. 准备配置文件

从示例文件复制并编辑 `token_pool_config.json`：

```bash
# 复制示例配置文件
cp token_pool_config-example.json token_pool_config.json
```

编辑 `token_pool_config.json`，填入你的 Perplexity 账户 token：

```json
{
  "heart_beat": {
    "enable": true,
    "question": "今天是几号？",
    "interval": 6,
    "tg_bot_token": "your-telegram-bot-token",
    "tg_chat_id": "your-telegram-chat-id"
  },
  "tokens": [
    {
      "id": "account1@example.com",
      "csrf_token": "your-csrf-token-1",
      "session_token": "your-session-token-1"
    },
    {
      "id": "account2@example.com",
      "csrf_token": "your-csrf-token-2",
      "session_token": "your-session-token-2"
    }
  ]
}
```

> **获取 Token 的方法：** 打开 perplexity.ai -> F12 开发者工具 -> Application -> Cookies
> - `csrf_token` 对应 `next-auth.csrf-token`
> - `session_token` 对应 `__Secure-next-auth.session-token`

### 心跳检测配置（可选）

心跳检测功能可以定期检查每个 token 的健康状态，并通过 Telegram 通知结果：

| 配置项 | 说明 |
|--------|------|
| `enable` | 是否启用心跳检测 |
| `question` | 用于检测的测试问题 |
| `interval` | 检测间隔时间（小时） |
| `tg_bot_token` | Telegram Bot Token（用于发送通知） |
| `tg_chat_id` | Telegram Chat ID（接收通知的聊天ID） |

> 如果不需要心跳检测功能，可以省略 `heart_beat` 配置或将 `enable` 设为 `false`

### 2. 启动服务

```bash
# 创建 .env 文件（可选）
cp token_pool_config-example.json token_pool_config.json

cp .env.example .env

# 启动服务
docker compose up -d
```

### docker-compose.yml 配置示例

```yml
services:
  perplexity-mcp:
    image: shancw/perplexity-mcp:latest
    container_name: perplexity-mcp
    ports:
      - "${MCP_PORT:-8000}:8000"
    environment:
      # MCP 认证密钥
      - MCP_TOKEN=${MCP_TOKEN:-sk-123456}
      # 管理员 Token（用于号池管理 API，可选）
      - PPLX_ADMIN_TOKEN=${PPLX_ADMIN_TOKEN:-}
      # SOCKS 代理配置 (可选)
      # 格式: socks5://[user[:pass]@]host[:port][#remark]
      # - SOCKS_PROXY=${SOCKS_PROXY:-}
    volumes:
      # 挂载 token 池配置文件
      - ./token_pool_config.json:/app/token_pool_config.json:ro
    restart: unless-stopped
```

### .env 环境变量

```bash
# Perplexity MCP Server 环境变量配置
# 复制此文件为 .env 并填入实际值

# ============================================
# MCP 服务配置
# ============================================

# MCP 服务端口
MCP_PORT=8000

# MCP API 认证密钥 (客户端需要在 Authorization header 中携带此密钥)
MCP_TOKEN=sk-123456

# 管理员 Token（用于号池管理 API：新增/删除 token 等操作）
PPLX_ADMIN_TOKEN=your-admin-token
```

---

## Vercel 部署

支持一键部署到 Vercel 平台，适合轻量使用场景。

### 部署步骤

1. Fork 本仓库
2. 在 Vercel 中导入项目
3. 配置环境变量：

| 环境变量 | 说明 | 示例 |
|----------|------|------|
| `MCP_TOKEN` | MCP API 认证密钥 | `sk-your-secret-key` |
| `PPLX_ADMIN_TOKEN` | 管理员 Token | `admin-secret-token` |
| `TOKEN_POOL_JSON` | Token 池配置 (JSON 字符串) | 见下方 |

**TOKEN_POOL_JSON 格式：**
```json
{"tokens":[{"id":"user1","csrf_token":"xxx","session_token":"yyy"}]}
```

### ⚠️ Vercel 上的 Token 保活

> **重要提示：** Vercel 是 Serverless 架构，实例会在空闲后被回收，内置的心跳循环无法持续运行。

**解决方案：使用 GitHub Actions 定时触发心跳**

1. 在仓库 **Settings → Secrets and variables → Actions** 中添加：
   - `VERCEL_URL`: 你的 Vercel 部署地址 (如 `https://your-app.vercel.app`)
   - `PPLX_ADMIN_TOKEN`: 管理员 Token

2. 项目已包含 `.github/workflows/heartbeat.yml`，会自动每 4 小时执行心跳检测

3. 也可以手动触发：进入 **Actions → Token Heartbeat → Run workflow**

### 保活建议

为了减少冷启动并保持 Token 活跃，建议同时配置：

| 服务 | 间隔 | 端点 | 作用 |
|------|------|------|------|
| UptimeRobot / cron-job.org | 5 分钟 | `/health` | 保持实例温热 |
| GitHub Actions | 4 小时 | `/heartbeat/test` | Token 保活 |

---

## 多token池配置（负载均衡）

支持配置多个 Perplexity 账户 token，实现负载均衡和高可用。

### 配置方式

1. 创建 JSON 配置文件 `token_pool_config.json`：
```json
{
  "tokens": [
    {
      "id": "user1",
      "csrf_token": "your-csrf-token-1",
      "session_token": "your-session-token-1"
    },
    {
      "id": "user2",
      "csrf_token": "your-csrf-token-2",
      "session_token": "your-session-token-2"
    }
  ]
}
```


## MCP 配置

```json
{
  "mcpServers": {
    "perplexity": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer sk-123456"
      }
    }
  }
}
```

## OpenAI 兼容端点


### 使用方式

**Base URL:** `http://127.0.0.1:8000/v1`

**认证:** 在请求头中添加 `Authorization: Bearer <MCP_TOKEN>`

#### 获取模型列表

```bash
curl http://127.0.0.1:8000/v1/models \
  -H "Authorization: Bearer sk-123456"
```

#### 聊天补全（非流式）

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-123456" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "perplexity-search",
    "messages": [{"role": "user", "content": "今天天气怎么样"}],
    "stream": false
  }'
```

#### 聊天补全（流式）

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-123456" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "perplexity-reasoning",
    "messages": [{"role": "user", "content": "分析一下人工智能的发展趋势"}],
    "stream": true
  }'
```

### 支持的模型

| 模型 ID | 模式 | 说明 |
|---------|------|------|
| **Search 模式（Pro）** | | |
| `perplexity-search` | pro | 默认搜索模型 |
| `sonar-search` | pro | Sonar 模型 |
| `gpt-5-2-search` | pro | GPT-5.2 |
| `claude-4-5-sonnet-search` | pro | Claude 4.5 Sonnet |
| `grok-4-1-search` | pro | Grok 4.1 |
| **Reasoning 模式** | | |
| `perplexity-reasoning` | reasoning | 默认推理模型 |
| `gpt-5-2-thinking-reasoning` | reasoning | GPT-5.2 Thinking |
| `claude-4-5-sonnet-thinking-reasoning` | reasoning | Claude 4.5 Sonnet Thinking |
| `gemini-3-0-pro-reasoning` | reasoning | Gemini 3.0 Pro |
| `kimi-k2-thinking-reasoning` | reasoning | Kimi K2 Thinking |
| `grok-4-1-reasoning-reasoning` | reasoning | Grok 4.1 Reasoning |
| **Deep Research 模式** | | |
| `perplexity-deepsearch` | deep research | 深度研究模型 |

### 客户端配置示例

以 ChatBox 为例：

1. 打开设置 → AI 模型提供商 → 添加自定义提供商
2. 填入：
   - API Host: `http://127.0.0.1:8000`
   - API Key: `sk-123456`（与 MCP_TOKEN 一致）
3. 选择模型如 `perplexity-search` 或 `perplexity-reasoning`

## 项目结构

```
perplexity/
├── server/                  # MCP 服务器模块
│   ├── __init__.py          # 包入口，导出主要组件
│   ├── main.py              # 服务启动入口
│   ├── app.py               # FastMCP 应用实例、认证中间件、核心查询逻辑
│   ├── mcp.py               # MCP 工具定义 (list_models, search, research)
│   ├── oai.py               # OpenAI 兼容 API (/v1/models, /v1/chat/completions)
│   ├── admin.py             # 管理端点 (健康检查、号池管理、心跳控制)
│   ├── utils.py             # 服务器专用工具函数 (验证、OAI模型映射)
│   ├── client_pool.py       # 多账户连接池管理
│   └── web/                 # 前端 Web UI (React + Vite)
│       ├── src/
│       │   ├── components/  # 组件
│       │   ├── hooks/       # React Hooks
│       │   ├── lib/
│       │   │   └── api.ts   # API 请求封装
│       │   ├── pages/
│       │   │   └── Playground.tsx  # Playground 页面
│       │   └── index.tsx    # 入口文件
│       └── vite.config.ts   # Vite 配置
├── client.py                # Perplexity API 客户端
├── config.py                # 配置常量
├── exceptions.py            # 自定义异常
├── logger.py                # 日志配置
└── utils.py                 # 通用工具函数 (重试、限流、JSON解析)
```

## 注册为 Claude Code 指令

复制 `.claude/commands/pp/` 目录下创建指令文件：

使用方式：
- `/pp:query 你的问题` - 快速搜索
- `/pp:reasoning 你的问题` - 推理模式，多步思考分析
- `/pp:research 你的问题` - 深度研究，最全面彻底
