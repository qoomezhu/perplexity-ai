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

# Perplexity AI MCP Server

> 非官方 Perplexity AI API，支持 MCP 协议和 OpenAI 兼容端点。

## 🚀 Hugging Face Space 部署指南

### 方式一：直接复制到新 Space

1. 在 HF 创建新 Space，选择 **Docker** SDK
2. 将本仓库代码推送到 Space
3. **重要**: 将 `Dockerfile.hf` 重命名为 `Dockerfile`
4. 将 `README_HF.md` 的 YAML 头部复制到你的 README.md 开头

### 方式二：使用 Git

```bash
# 克隆仓库
git clone https://github.com/qoomezhu/perplexity-ai
cd perplexity-ai

# 使用 HF 专用 Dockerfile
cp Dockerfile.hf Dockerfile

# 添加 HF remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/perplexity-mcp

# 推送
git push hf main
```

## 🔧 配置 Secrets

在 Space **Settings** → **Repository secrets** 中添加:

| Secret 名称 | 说明 | 必填 |
|------------|------|-----|
| `MCP_TOKEN` | API 认证密钥 (如: `sk-xxxxx`) | ✅ |
| `PPLX_ADMIN_TOKEN` | 管理员 Token（用于 /heartbeat/* /pool/* 这类管理接口） | 🔸 建议 |
| `TOKEN_POOL_JSON` | 完整 Token 池 JSON 配置 | 🔸 二选一 |
| `PPLX_CSRF_TOKEN` | 单个 CSRF Token（优先使用） | 🔸 二选一 |
| `PPLX_NEXT_AUTH_CSRF_TOKEN` | 单个 CSRF Token（兼容旧变量名） | 🔸 二选一 |
| `PPLX_SESSION_TOKEN` | 单个 Session Token | 🔸 二选一 |

### TOKEN_POOL_JSON 格式

```json
{"tokens":[{"id":"user1","csrf_token":"your-csrf-token","session_token":"your-session-token"}]}
```

> **获取 Token**: 打开 perplexity.ai → F12 开发者工具 → Application → Cookies
> - `csrf_token` = `next-auth.csrf-token`
> - `session_token` = `__Secure-next-auth.session-token`

## 📡 API 使用

部署成功后，你的 API 地址为: `https://YOUR-USERNAME-SPACE-NAME.hf.space`

### 健康检查

```bash
curl https://YOUR-SPACE.hf.space/health
```

### MCP 配置

```json
{
  "mcpServers": {
    "perplexity": {
      "type": "http",
      "url": "https://YOUR-SPACE.hf.space/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

### OpenAI 兼容端点

```bash
# 获取模型列表
curl https://YOUR-SPACE.hf.space/v1/models \
  -H "Authorization: Bearer YOUR_MCP_TOKEN"

# 聊天补全
curl https://YOUR-SPACE.hf.space/v1/chat/completions \
  -H "Authorization: Bearer YOUR_MCP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "perplexity-search",
    "messages": [{"role": "user", "content": "今天天气怎么样"}],
    "stream": false
  }'
```

## ⚠️ 注意事项

### 冷启动

HF Space 免费版会在空闲后休眠，首次请求需等待 ~30 秒。

### Token 保活（重要）

- `/health` 只能用于 **Space 保活（防休眠）**，不会验证 Perplexity 账号是否仍处于登录态。
- `/heartbeat/test` 用于 **Token 检测/保活**：会先检查 `https://www.perplexity.ai/api/auth/session` 是否仍登录（必须有 `user`），再做一次轻量请求（`auto` 模式，且 `incognito=false`）。

> 注意：如果 Perplexity 的 session cookie 存在“绝对过期”（例如 ~48h），任何 keepalive 都不保证永久有效，只能在可续期的窗口内尽量延长，或定期更新 token。

建议使用外部 cron 服务:

| 服务 | 间隔 | 端点 | 作用 |
|------|------|------|------|
| [cron-job.org](https://cron-job.org) | 5 分钟 | `/health` | 防止休眠 |
| GitHub Actions / 其它支持 Header 的 Cron | 4 小时 | `/heartbeat/test` | Token 检测/保活（需 `X-Admin-Token`） |

示例（/heartbeat/test）：

```bash
curl -X POST https://YOUR-SPACE.hf.space/heartbeat/test \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: YOUR_PPLX_ADMIN_TOKEN" \
  -d '{}'
```

### 资源限制

| 类型 | 免费版 | 升级版 |
|------|-------|-------|
| CPU | 2 核 | 可选更多 |
| RAM | 16 GB | 可选更多 |
| 存储 | 50 GB | 可选更多 |

## 🔗 相关链接

- [源项目](https://github.com/qoomezhu/perplexity-ai)
- [Hugging Face Spaces 文档](https://huggingface.co/docs/hub/spaces-sdks-docker)
