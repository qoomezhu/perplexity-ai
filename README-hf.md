---
title: Perplexity MCP Server
emoji: 🔎
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Hugging Face Spaces 部署指南

本指南用于将 Perplexity MCP Server 部署到 Hugging Face Spaces（Docker），并适配**无持久卷**场景。

## 一、前提条件

1. Hugging Face 账户
2. 已创建 Space（Docker SDK）
3. Perplexity 账户的 `csrf_token` 与 `session_token`

## 二、创建 Space

1. 打开 https://huggingface.co/spaces/new
2. 选择：
   - SDK: **Docker**
   - Space Name: 例如 `ppl`
   - Visibility: Public / Private

## 三、配置 Secrets（关键）

在 Space -> Settings -> Secrets 添加：

- `MCP_TOKEN`：API 访问 Bearer Token（务必使用高强度随机值）
- `PPLX_ADMIN_TOKEN`：管理接口 Token
- `PPLX_TOKEN_POOL_CONFIG`：**JSON 字符串**（不需要持久卷）

示例（单行 JSON）：

```json
{"heart_beat":{"enable":false},"fallback":{"fallback_to_auto":true},"incognito":{"enabled":true},"tokens":[{"id":"account1@example.com","csrf_token":"your-csrf-token","session_token":"your-session-token"}]}
```

> 当前已支持：`PPLX_TOKEN_POOL_CONFIG` 可以是文件路径 / JSON 字符串 / Base64 JSON。

## 四、保活策略

### 推荐：外部 Cron（有效）

使用你自己的外部 cronjob（或 GitHub Actions schedule）每 5 分钟请求：

```bash
curl -fsS --max-time 20 https://<your-space>.hf.space/health >/dev/null
```

### 说明

容器内 cron 只能在容器已运行时执行，不能保证防止 Space 冷休眠。
外部 cron 更可靠。

## 五、访问地址

- 主服务：`https://<space>.hf.space/`
- 管理界面：`https://<space>.hf.space/admin/`
- Playground：`https://<space>.hf.space/playground/`
- 健康检查：`https://<space>.hf.space/health`
- OpenAI 模型列表：`https://<space>.hf.space/v1/models`

## 六、常见问题

1. **服务启动失败**：检查 Space Build Logs 与 Secrets JSON 格式。
2. **匿名模式运行**：通常是 `PPLX_TOKEN_POOL_CONFIG` 未正确解析。
3. **Token 失效**：重新抓取 Perplexity cookies 并更新 Secrets。
