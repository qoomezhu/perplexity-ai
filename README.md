---
title: Perplexity AI MCP Server
emoji: ""
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

## 源项目地址：
https://github.com/helallao/perplexity-ai

## Hugging Face Spaces（手机可部署，无需电脑）

你截图里的 400 报错是因为 `https://huggingface.co/new-space?template=...` 的 `template` 参数只接受 Hugging Face 官方内置模板，不支持直接用 GitHub 仓库当 template。

推荐方式：用 GitHub Actions 把本仓库自动同步到你的 Hugging Face Space（一次设置，之后每次 push 自动部署）。

### A. 在 Hugging Face 创建 Space
1. 打开 https://huggingface.co/new-space
2. SDK 选择 **Docker**
3. Space name 自己取（例如 `perplexity-mcp`）

### B. 在 Space 里设置 Secrets
Space → Settings → Repository secrets：
- `MCP_TOKEN`：访问鉴权 token
- `TOKEN_POOL_JSON`：形如 `{"tokens":[{"id":"u1","csrf_token":"xxx","session_token":"yyy"}]}`

### C. 在 GitHub 仓库设置 Actions Secrets（用于自动同步到 HF）
GitHub → Settings → Secrets and variables → Actions：
- `HF_TOKEN`：你的 Hugging Face Access Token（需要 write 权限）
- `HF_USERNAME`：你的 Hugging Face 用户名
- `HF_SPACE`：你刚创建的 Space 名（不含用户名）

然后在 GitHub 的 Actions 标签页里手动运行一次 “Sync to Hugging Face Space”，或任意提交一次代码，即会触发同步。

---

## 展示
ADMIN
<img width="1751" height="900" alt="image" src="https://github.com/user-attachments/assets/baa6d6e0-1752-42e6-9eda-29930f8b9947" />

OAI playground
![img_v3_02u3_eada7873-379e-42c1-bcbf-3c0466a66ffg](https://github.com/user-attachments/assets/29d75f8e-2058-4945-b486-d50b09f140a1)

MCP
<img width="1894" height="989" alt="image" src="https://github.com/user-attachments/assets/4a495432-8305-4820-8b4a-d7e54986ba45" />


## 更新记录
+ 2026-01-28：添加 Hugging Face Space Docker 部署支持（含 GitHub Actions 同步）
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
