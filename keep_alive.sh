#!/bin/bash
# Hugging Face Spaces 保活脚本
# 定期访问健康检查端点，防止服务休眠

# 配置
HEALTH_URL="http://localhost:7860/health"
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

# 检查服务是否运行
check_service() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null)
    if [ "$response" = "200" ]; then
        echo "$LOG_PREFIX 服务运行正常 (HTTP $response)"
        return 0
    else
        echo "$LOG_PREFIX 服务异常 (HTTP $response)"
        return 1
    fi
}

# 保活请求
keep_alive() {
    local response=$(curl -s "$HEALTH_URL" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "$LOG_PREFIX 保活成功: $response"
    else
        echo "$LOG_PREFIX 保活失败"
    fi
}

# 主逻辑
main() {
    echo "$LOG_PREFIX 开始保活检查..."
    
    if check_service; then
        keep_alive
    else
        echo "$LOG_PREFIX 服务未运行，尝试重启..."
        # 这里可以添加重启逻辑，但在Hugging Face Spaces中通常不需要
        # 因为服务会自动重启
    fi
    
    echo "$LOG_PREFIX 保活检查完成"
}

# 执行主函数
main