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

## 📱 手机部署指南（针对 qoomezhu）

由于 Hugging Face 官方限制，无法直接通过链接一键部署。请按以下步骤操作（全程手机网页即可完成）：

### 第1步：在 Hugging Face 创建 Space
1. 打开 [Create New Space](https://huggingface.co/new-space)
2. 填写信息：
   - **Space name**: `perplexity-mcp`
   - **License**: `mit`
   - **SDK**: 选择 **Docker** (必须选这个)
   - **Space hardware**: `CPU basic` (免费)
   - **Visibility**: `Public` 或 `Private`
3. 点击 **Create Space**

### 第2步：配置 Space 环境变量 (Secrets)
进入你刚创建的 Space (`qoomezhu/perplexity-mcp`) -> **Settings** -> **Repository secrets** -> **New secret**：

| Name | Value (示例) |
|------|-------------|
| `MCP_TOKEN` | `sk-123456` (你自己设定的密钥) |
| `TOKEN_POOL_JSON` | `{"tokens":[{"id":"u1","csrf_token":"xxx","session_token":"yyy"}]}` |

> **如何获取 Token**: 手机浏览器登录 perplexity.ai -> 菜单 -> 桌面版网站 -> 开发者工具 -> Application -> Cookies
> - `csrf_token` 对应 `next-auth.csrf-token`
> - `session_token` 对应 `__Secure-next-auth.session-token`

### 第3步：连接 GitHub 自动部署
回到本 GitHub 仓库 -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**：

| Name | Value | 说明 |
|------|-------|------|
| `HF_TOKEN` | `hf_xxxx` | 你的 HF Access Token (需 Write 权限) |
| `HF_USERNAME` | `qoomezhu` | 你的 HF 用户名 |
| `HF_SPACE` | `perplexity-mcp` | 你的 Space 名称 |

> **获取 HF_TOKEN**: [Hugging Face Settings -> Access Tokens](https://huggingface.co/settings/tokens) -> Create new token -> 勾选 "Write" 权限

### 第4步：触发部署
1. 点击本仓库上方的 **Actions** 标签页
2. 点击左侧 **Sync to Hugging Face Space**
3. 点击右侧 **Run workflow** -> **Run workflow**

等待约 2-3 分钟，Action 显示绿色对勾 ✅ 后，你的 Space 就会自动开始构建并运行！

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
> - `session_token` = `__Secure-next-auth.session-token`

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
