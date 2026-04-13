#!/bin/bash
# Hermes Agent 入口脚本

set -e

echo "🚀 Starting Hermes Agent..."

# 等待依赖服务启动
wait_for_redis() {
    echo "⏳ Waiting for Redis..."
    until redis-cli -h redis ping 2>/dev/null | grep -q PONG; do
        sleep 2
    done
    echo "✅ Redis is ready"
}

wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL..."
    until pg_isready -h postgres -U hermes -d hermes 2>/dev/null; do
        sleep 2
    done
    echo "✅ PostgreSQL is ready"
}

# 初始化 Hermes 数据目录
init_hermes_dirs() {
    echo "📁 Initializing Hermes directories..."
    mkdir -p ${HERMES_HOME}/logs
    mkdir -p ${HERMES_HOME}/data/sessions
    mkdir -p ${HERMES_HOME}/data/knowledge
    mkdir -p ${HERMES_HOME}/cache
}

# 根据命令执行不同操作
case "${1:-hermes}" in
    hermes)
        echo "📦 Starting Hermes in server mode..."
        wait_for_redis &
        wait_for_postgres &
        init_hermes_dirs
        exec python -m hermes.server --host 0.0.0.0 --port 8080
        ;;
    start)
        echo "📦 Starting Hermes in background mode..."
        wait_for_redis &
        wait_for_postgres &
        init_hermes_dirs
        exec python -m hermes.server --host 0.0.0.0 --port 8080
        ;;
    dev)
        echo "🔧 Starting Hermes in development mode..."
        wait_for_redis &
        wait_for_postgres &
        init_hermes_dirs
        exec python -m hermes.server --dev --host 0.0.0.0 --port 8080
        ;;
    shell)
        echo "🐚 Starting Hermes interactive shell..."
        exec python -m hermes.shell
        ;;
    *)
        echo "Usage: entrypoint.sh {hermes|start|dev|shell}"
        exit 1
        ;;
esac
