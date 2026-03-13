# Hugging Face Spaces 配置说明

## 环境变量配置

在 Hugging Face Space 的 Settings → Repository secrets 中添加以下环境变量：

### 必需配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `MCP_TOKEN` | MCP 服务认证令牌 | `sk-123456` |
| `PPLX_ADMIN_TOKEN` | 管理界面认证令牌 | `your-admin-token` |

### Token 池配置

有两种方式配置 Token 池：

#### 方式1：通过环境变量（推荐）

在 Secrets 中添加 `PPLX_TOKEN_POOL_CONFIG` 变量，值为 JSON 字符串：

```json
{
  "heart_beat": {
    "enable": true,
    "question": "今天是几号？",
    "interval": 6,
    "tg_bot_token": "",
    "tg_chat_id": ""
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

#### 方式2：通过文件上传

1. 创建 `token_pool_config.json` 文件
2. 将文件上传到 Space 仓库根目录
3. 设置环境变量 `PPLX_TOKEN_POOL_CONFIG=/app/token_pool_config.json`

### 可选配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务端口 | `7860` |
| `SOCKS_PROXY` | SOCKS 代理 | 无 |

## 获取 Perplexity Token

1. 登录 [perplexity.ai](https://perplexity.ai)
2. 按 F12 打开开发者工具
3. 转到 Application → Cookies
4. 复制以下值：
   - `next-auth.csrf-token` → `csrf_token`
   - `__Secure-next-auth.session-token` → `session_token`

## 保活机制

本部署包含自动保活机制：

1. **Cron 任务**: 每 5 分钟访问健康检查端点
2. **健康检查**: `/health` 端点返回服务状态
3. **日志记录**: 保活日志保存在 `/var/log/keep_alive.log`

## 部署步骤

1. 创建 Hugging Face Docker Space
2. 配置 Secrets（见上文）
3. 推送代码到 Space 仓库
4. 等待构建完成
5. 访问 Space URL 检查服务状态

## 服务端点

部署成功后，您可以通过以下 URL 访问服务：

- **主服务**: `https://your-username-your-space-name.hf.space/`
- **管理界面**: `https://your-username-your-space-name.hf.space/admin/`
- **Playground**: `https://your-username-your-space-name.hf.space/playground/`
- **健康检查**: `https://your-username-your-space-name.hf.space/health`
- **API 文档**: `https://your-username-your-space-name.hf.space/v1/models`

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