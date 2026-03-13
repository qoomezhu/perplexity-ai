#!/bin/bash
# Hugging Face Spaces 部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        log_error "git 未安装"
        exit 1
    fi
    
    # 检查 docker
    if ! command -v docker &> /dev/null; then
        log_warn "docker 未安装，将跳过本地测试"
    fi
    
    log_info "依赖检查完成"
}

# 配置变量
setup_variables() {
    log_info "配置变量..."
    
    # Hugging Face Space 信息
    read -p "请输入 Hugging Face 用户名: " HF_USERNAME
    read -p "请输入 Space 名称: " HF_SPACE_NAME
    
    if [ -z "$HF_USERNAME" ] || [ -z "$HF_SPACE_NAME" ]; then
        log_error "用户名和 Space 名称不能为空"
        exit 1
    fi
    
    HF_SPACE_URL="https://huggingface.co/spaces/${HF_USERNAME}/${HF_SPACE_NAME}"
    HF_GIT_URL="https://huggingface.co/spaces/${HF_USERNAME}/${HF_SPACE_NAME}"
    
    log_info "Space URL: ${HF_SPACE_URL}"
}

# 准备文件
prepare_files() {
    log_info "准备部署文件..."
    
    # 复制 Hugging Face Dockerfile
    if [ -f "Dockerfile.hf" ]; then
        cp Dockerfile.hf Dockerfile
        log_info "已复制 Dockerfile.hf 为 Dockerfile"
    else
        log_warn "Dockerfile.hf 不存在，使用默认 Dockerfile"
    fi
    
    # 确保保活脚本可执行
    if [ -f "keep_alive.sh" ]; then
        chmod +x keep_alive.sh
        log_info "已设置 keep_alive.sh 可执行权限"
    fi
    
    # 创建 .dockerignore（如果不存在）
    if [ ! -f ".dockerignore" ]; then
        cat > .dockerignore << EOF
.git
.gitignore
__pycache__
*.pyc
.DS_Store
*.env
.env.*
!env.example
venv/
node_modules/
dist/
build/
*.log
EOF
        log_info "已创建 .dockerignore"
    fi
}

# 本地测试
local_test() {
    if command -v docker &> /dev/null; then
        log_info "进行本地 Docker 测试..."
        
        # 构建镜像
        docker build -t perplexity-mcp-hf .
        
        # 运行容器（后台）
        docker run -d \
            --name perplexity-mcp-test \
            -p 7860:7860 \
            -e MCP_TOKEN=sk-test \
            -e PPLX_ADMIN_TOKEN=test-admin \
            perplexity-mcp-hf
        
        # 等待服务启动
        sleep 5
        
        # 测试健康检查
        if curl -f http://localhost:7860/health > /dev/null 2>&1; then
            log_info "本地测试成功"
        else
            log_warn "本地测试失败，但继续部署"
        fi
        
        # 停止并删除容器
        docker stop perplexity-mcp-test
        docker rm perplexity-mcp-test
    else
        log_warn "跳过本地测试（docker 未安装）"
    fi
}

# 部署到 Hugging Face
deploy_to_hf() {
    log_info "部署到 Hugging Face Spaces..."
    
    # 检查是否已存在 git 仓库
    if [ -d ".git" ]; then
        log_info "检测到现有 git 仓库"
    else
        log_info "初始化 git 仓库"
        git init
    fi
    
    # 添加 Hugging Face 远程仓库
    if git remote get-url hf > /dev/null 2>&1; then
        log_info "更新 Hugging Face 远程仓库"
        git remote set-url hf "${HF_GIT_URL}"
    else
        log_info "添加 Hugging Face 远程仓库"
        git remote add hf "${HF_GIT_URL}"
    fi
    
    # 添加所有文件
    git add .
    
    # 提交更改
    git commit -m "Deploy to Hugging Face Spaces" || log_warn "没有新的更改需要提交"
    
    # 推送到 Hugging Face
    log_info "推送到 Hugging Face..."
    git push hf main --force
    
    log_info "部署完成！"
    log_info "访问您的 Space: ${HF_SPACE_URL}"
}

# 显示部署信息
show_deployment_info() {
    log_info "部署信息："
    echo "=========================================="
    echo "Space URL: ${HF_SPACE_URL}"
    echo "管理界面: ${HF_SPACE_URL}/admin/"
    echo "Playground: ${HF_SPACE_URL}/playground/"
    echo "健康检查: ${HF_SPACE_URL}/health"
    echo "API 文档: ${HF_SPACE_URL}/v1/models"
    echo "=========================================="
    echo ""
    log_info "下一步："
    echo "1. 在 Space 设置中添加 Secrets："
    echo "   - MCP_TOKEN"
    echo "   - PPLX_ADMIN_TOKEN"
    echo "   - PPLX_TOKEN_POOL_CONFIG"
    echo "2. 等待构建完成（通常需要 5-10 分钟）"
    echo "3. 访问 Space URL 检查服务状态"
}

# 主函数
main() {
    log_info "开始 Hugging Face Spaces 部署..."
    
    check_dependencies
    setup_variables
    prepare_files
    local_test
    deploy_to_hf
    show_deployment_info
    
    log_info "部署脚本执行完成！"
}

# 执行主函数
main "$@"