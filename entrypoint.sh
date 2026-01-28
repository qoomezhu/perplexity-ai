#!/bin/bash
set -e

CONFIG_FILE="/home/user/app/config/token_pool_config.json"

# ========================================
# 从环境变量生成 token_pool_config.json
# HF Space 的 Secrets 会注入为环境变量
# ========================================

echo "🔧 Perplexity MCP Server for Hugging Face Space"
echo "================================================"

# 确保配置目录存在 (关键修复)
mkdir -p "$(dirname "$CONFIG_FILE")"

if [ -n "$TOKEN_POOL_JSON" ]; then
    echo "📝 从 TOKEN_POOL_JSON 环境变量生成配置..."
    echo "$TOKEN_POOL_JSON" > "$CONFIG_FILE"
    echo "✅ Token 池配置已生成"
elif [ -n "$PPLX_CSRF_TOKEN" ] && [ -n "$PPLX_SESSION_TOKEN" ]; then
    echo "📝 从单独 token 环境变量生成配置..."
    cat > "$CONFIG_FILE" << EOF
{
  "heart_beat": {
    "enable": false
  },
  "tokens": [
    {
      "id": "${PPLX_TOKEN_ID:-default}",
      "csrf_token": "${PPLX_CSRF_TOKEN}",
      "session_token": "${PPLX_SESSION_TOKEN}"
    }
  ]
}
EOF
    echo "✅ 单 Token 配置已生成"
else
    echo "⚠️  警告: 未设置 token 环境变量"
    echo "   请在 HF Space Settings -> Secrets 中配置:"
    echo "   - TOKEN_POOL_JSON (完整 JSON)"
    echo "   或"
    echo "   - PPLX_CSRF_TOKEN + PPLX_SESSION_TOKEN"
    echo ""
    echo "📝 使用空配置启动（功能受限）..."
    echo '{"tokens":[]}' > "$CONFIG_FILE"
fi

echo ""
echo "🚀 启动 Perplexity MCP Server"
echo "   端口: 7860"
echo "   健康检查: /health"
echo "   MCP 端点: /mcp"
echo "   OpenAI 兼容: /v1/chat/completions"
echo "================================================"
echo ""

exec python -m perplexity.server --host 0.0.0.0 --port 7860
