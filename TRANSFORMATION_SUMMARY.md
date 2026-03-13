# Hugging Face Spaces 改造总结

## 改造目标

将 Perplexity MCP Server 改造为适合部署在 Hugging Face Spaces 上，使用 cronjob 保活，不需要持久卷。

## 改造内容

### 1. Dockerfile 改造

#### 新增文件：`Dockerfile.hf`
- 专为 Hugging Face Spaces 优化的 Dockerfile
- 添加 cron 支持用于保活机制
- 端口改为 7860（Hugging Face Spaces 默认端口）
- 添加保活脚本和 cron 任务

#### 更新文件：`Dockerfile`
- 支持可配置的端口（通过环境变量 `PORT`）
- 保持向后兼容性

### 2. 保活机制

#### 新增文件：`keep_alive.sh`
- 定期访问健康检查端点 `/health`
- 每 5 分钟执行一次（通过 cron）
- 记录保活日志到 `/var/log/keep_alive.log`

### 3. 配置管理

#### 新增文件：`.env.hf.example`
- Hugging Face Spaces 环境变量配置示例
- 包含所有必需的配置项

#### 新增文件：`SPACE_CONFIG.md`
- Hugging Face Spaces 配置详细说明
- 包含环境变量配置、Token 获取方法等

### 4. 部署脚本

#### 新增文件：`deploy_hf.sh`
- 自动化部署脚本
- 包含依赖检查、文件准备、本地测试、部署到 Hugging Face 等步骤

### 5. 文档更新

#### 新增文件：`README-hf.md`
- Hugging Face Spaces 部署详细指南
- 包含部署步骤、配置说明、故障排除等

#### 更新文件：`README.md`
- 添加 Hugging Face Spaces 部署信息
- 更新 changelog

### 6. 代码修改

#### 更新文件：`perplexity/server/main.py`
- 支持通过环境变量 `PORT` 配置端口
- 保持命令行参数的向后兼容性

#### 更新文件：`docker-compose.yml`
- 支持可配置的端口
- 添加环境变量支持

## 部署流程

### 1. 创建 Hugging Face Space
1. 访问 [huggingface.co/spaces/new](https://huggingface.co/spaces/new)
2. 选择 "Docker" SDK
3. 创建 Space

### 2. 配置 Secrets
在 Space 设置中添加以下 Secrets：
- `MCP_TOKEN`: MCP 服务认证令牌
- `PPLX_ADMIN_TOKEN`: 管理界面认证令牌
- `PPLX_TOKEN_POOL_CONFIG`: Token 池配置（JSON 格式）

### 3. 部署代码
```bash
# 使用部署脚本
./deploy_hf.sh

# 或手动部署
git init
git remote add hf https://huggingface.co/spaces/your-username/your-space-name
git add .
git commit -m "Deploy to Hugging Face Spaces"
git push hf main --force
```

### 4. 访问服务
- 主服务: `https://your-username-your-space-name.hf.space/`
- 管理界面: `https://your-username-your-space-name.hf.space/admin/`
- Playground: `https://your-username-your-space-name.hf.space/playground/`
- 健康检查: `https://your-username-your-space-name.hf.space/health`

## 保活机制说明

### 工作原理
1. **Cron 任务**: 每 5 分钟执行一次 `keep_alive.sh` 脚本
2. **健康检查**: 脚本访问 `/health` 端点检查服务状态
3. **日志记录**: 保活日志保存在 `/var/log/keep_alive.log`

### 配置
- Cron 任务在 Dockerfile 中配置
- 保活间隔：5 分钟（可修改）
- 健康检查端点：`/health`

## 注意事项

### 1. 免费 tier 限制
- Hugging Face Spaces 免费 tier 有资源限制
- 保活机制可以减少休眠，但不能完全避免

### 2. 数据持久性
- 本部署不使用持久卷
- 重启后数据会丢失
- Token 配置通过环境变量或文件上传

### 3. 安全
- 请妥善保管您的 Token 和 API 密钥
- 使用 Secrets 管理敏感信息

### 4. 端口配置
- Hugging Face Spaces 默认使用 7860 端口
- 通过环境变量 `PORT` 配置
- 在 Dockerfile 中设置 `EXPOSE ${PORT}`

## 文件清单

### 新增文件
1. `Dockerfile.hf` - Hugging Face Spaces 专用 Dockerfile
2. `keep_alive.sh` - 保活脚本
3. `.env.hf.example` - 环境变量配置示例
4. `SPACE_CONFIG.md` - 配置说明文档
5. `deploy_hf.sh` - 部署脚本
6. `README-hf.md` - Hugging Face Spaces 部署指南
7. `TRANSFORMATION_SUMMARY.md` - 本文件

### 更新文件
1. `Dockerfile` - 支持可配置端口
2. `docker-compose.yml` - 支持可配置端口和环境变量
3. `perplexity/server/main.py` - 支持 PORT 环境变量
4. `README.md` - 添加 Hugging Face Spaces 部署信息

## 测试

### 本地测试
```bash
# 构建镜像
docker build -t perplexity-mcp-hf -f Dockerfile.hf .

# 运行容器
docker run -d \
  --name perplexity-mcp-test \
  -p 7860:7860 \
  -e MCP_TOKEN=sk-test \
  -e PPLX_ADMIN_TOKEN=test-admin \
  perplexity-mcp-hf

# 测试健康检查
curl http://localhost:7860/health

# 查看日志
docker logs perplexity-mcp-test
```

### 部署后测试
1. 访问健康检查端点：`https://your-space-url.hf.space/health`
2. 访问管理界面：`https://your-space-url.hf.space/admin/`
3. 测试 API：`https://your-space-url.hf.space/v1/models`

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

## 总结

通过以上改造，Perplexity MCP Server 现在可以成功部署到 Hugging Face Spaces 上，并具备以下特性：

1. **兼容性**: 支持 Hugging Face Spaces 的 Docker 部署
2. **保活机制**: 使用 cronjob 定期访问健康检查端点
3. **无持久卷**: 通过环境变量管理配置，不需要持久卷
4. **自动化部署**: 提供部署脚本简化部署流程
5. **完整文档**: 提供详细的部署和配置文档

改造后的项目保持了原有功能，同时增加了 Hugging Face Spaces 的部署支持，使用户可以更方便地在云端部署和使用 Perplexity MCP Server。