# Hugging Face Spaces 配置说明

## 1) 必需 Secrets

在 Hugging Face Space 的 **Settings -> Secrets** 配置：

| Key | 说明 |
|---|---|
| `MCP_TOKEN` | MCP/OpenAI 接口鉴权 Bearer Token |
| `PPLX_ADMIN_TOKEN` | 管理接口鉴权 Token |
| `PPLX_TOKEN_POOL_CONFIG` | Token 池配置（推荐 JSON 字符串） |

## 2) `PPLX_TOKEN_POOL_CONFIG` 支持格式

按优先级支持：

1. 文件路径（例如 `/app/token_pool_config.json`）
2. JSON 字符串（推荐，适合无持久卷）
3. Base64 编码 JSON 字符串

### 推荐示例（单行 JSON）

```json
{"heart_beat":{"enable":false},"fallback":{"fallback_to_auto":true},"incognito":{"enabled":true},"tokens":[{"id":"account1@example.com","csrf_token":"your-csrf-token","session_token":"your-session-token"}]}
```

## 3) 保活建议

- **推荐外部 cronjob** 每 5 分钟访问 `/health`
- 不依赖持久卷
- 若使用 GitHub Actions，可用 schedule 工作流定时请求

## 4) URL 列表

- `/health`
- `/admin/`
- `/playground/`
- `/v1/models`

## 5) 注意事项

1. 免费资源会冷启动，外部保活可降低休眠概率。  
2. 无持久卷场景下，运行时改 token 在重启后会丢失。  
3. 请定期轮换 Perplexity token。  
