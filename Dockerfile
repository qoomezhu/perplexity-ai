# ============================================
# Hugging Face Spaces Docker Deployment
# 端口: 7860 | 用户: non-root
# ============================================

# ============ 阶段1: 前端构建 ============
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY perplexity/server/web/package*.json ./
RUN npm ci --prefer-offline --no-audit 2>/dev/null || npm install
COPY perplexity/server/web/ ./
RUN npm run build

# ============ 阶段2: Python 运行时 ============
FROM python:3.12-slim

ENV PORT=7860
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user/app

# 安装 Python 依赖
COPY --chown=user pyproject.toml README.md ./
COPY --chown=user perplexity/ ./perplexity/
COPY --chown=user perplexity_async/ ./perplexity_async/
RUN pip install --no-cache-dir --user .

# 复制前端构建产物
COPY --from=frontend-builder --chown=user /frontend/dist ./perplexity/server/web/dist

# 复制启动脚本
COPY --chown=user entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENV PPLX_TOKEN_POOL_CONFIG=/home/user/app/token_pool_config.json
ENV PYTHONUNBUFFERED=1

EXPOSE 7860
CMD ["./entrypoint.sh"]
