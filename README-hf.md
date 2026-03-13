# Hugging Face Spaces 部署指南

本指南将帮助您将 Perplexity MCP Server 部署到 Hugging Face Spaces。

## 前提条件

1. Hugging Face 账户
2. Perplexity AI 账户的 CSRF Token 和 Session Token

## 部署步骤

### 1. 创建 Hugging Face Space

1. 访问 [huggingface.co/spaces/new](https://huggingface.co/spaces/new)
2. 填写以下信息：
   - **Space name**: 选择一个名称（如 `perplexity-mcp-server`）
   - **Owner**: 您的账户或组织
   - **Visibility**: Public 或 Private
   - **Space SDK**: 选择 **"Docker"**
   - **Hardware**: 选择适当的硬件（免费 tier 通常足够）
3. 点击 "Create Space"

### 2. 配置 Secrets

在 Space 设置中添加以下 Secrets：

1. **MCP_TOKEN**: 您的 API 认证令牌（默认: `sk-123456`）
2. **PPLX_ADMIN_TOKEN**: 管理员令牌（用于管理界面）
3. **PPLX_TOKEN_POOL_CONFIG**: Token 池配置（JSON 格式）

### 3. Token 池配置示例

在 `PPLX_TOKEN_POOL_CONFIG` Secret 中添加以下 JSON 配置：

```json
{
  "heart_beat": {
    "enable": true,
    "question": "今天是几号？",
    "interval": 6,
    "tg_bot_token": "your-telegram-bot-token",
    "tg_chat_id": "your-telegram-chat-id"
  },
  "fallback": {
    "fallback_to_auto": true
  },
  "tokens": [
    {
      "id": "account1@example.com",
      "csrf_token": "your-csrf-token-1",
      "session_token": "your-session-token-1"
    }
  ]
}
```

### 4. 获取 Perplexity Token

1. 登录 [perplexity.ai](https://perplexity.ai)
2. 按 F12 打开开发者工具
3. 转到 Application → Cookies
4. 复制以下值：
   - `next-auth.csrf-token` → `csrf_token`
   - `__Secure-next-auth.session-token` → `session_token`

### 5. 部署代码

将以下文件推送到您的 Space 仓库：

1. `Dockerfile.hf` → 重命名为 `Dockerfile`
2. `keep_alive.sh`
3. 所有项目代码

### 6. 环境变量配置

在 Space 设置中配置以下环境变量：

- `PORT=7860`（Hugging Face Spaces 默认端口）
- `MCP_TOKEN=your-mcp-token`
- `PPLX_ADMIN_TOKEN=your-admin-token`

## 保活机制

本部署包含自动保活机制：

1. **Cron 任务**: 每 5 分钟访问健康检查端点
2. **健康检查**: `/health` 端点返回服务状态
3. **日志记录**: 保活日志保存在 `/var/log/keep_alive.log`

## 访问服务

部署成功后，您可以通过以下 URL 访问服务：

- **主服务**: `https://your-username-your-space-name.hf.space/`
- **管理界面**: `https://your-username-your-space-name.hf.space/admin/`
- **Playground**: `https://your-username-your-space-name.hf.space/playground/`
- **健康检查**: `https://your-username-your-space-name.hf.space/health`
- **API 文档**: `https://your-username-your-space-name.hf.space/v1/models`

## API 使用示例

### MCP 端点

```bash
curl -X POST https://your-space-url.hf.space/mcp \
  -H "Authorization: Bearer your-mcp-token" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "search", "arguments": {"query": "What is AI?"}}}'
```

### OpenAI 兼容端点

```bash
curl https://your-space-url.hf.space/v1/chat/completions \
  -H "Authorization: Bearer your-mcp-token" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "perplexity-search",
    "messages": [{"role": "user", "content": "What is the weather today?"}],
    "stream": false
  }'
```

## 故障排除

### 1. 服务无法启动

- 检查 Space 日志中的错误信息
- 确保所有必需的 Secrets 已正确配置
- 验证 Token 配置 JSON 格式是否正确

### 2. 保活不工作

- 检查 `/var/log/keep_alive.log` 日志
- 确保 cron 服务正在运行
- 验证健康检查端点是否可访问

### 3. Token 过期

- 定期更新 Perplexity Token
- 使用管理界面或 API 更新 Token 配置

## 注意事项

1. **免费 tier 限制**: Hugging Face Spaces 免费 tier 有资源限制
2. **休眠策略**: 免费 Space 在不活动时会休眠，保活机制可以减少休眠
3. **数据持久性**: 本部署不使用持久卷，重启后数据会丢失
4. **安全**: 请妥善保管您的 Token 和 API 密钥

## 更新部署

要更新部署：

1. 修改代码并推送到 Space 仓库
2. Hugging Face 会自动重新构建和部署
3. 检查 Space 日志确保更新成功

## 支持

如有问题，请检查：
1. Hugging Face Space 日志
2. 应用日志 (`/var/log/keep_alive.log`)
3. 健康检查端点状态