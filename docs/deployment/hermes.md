# Hermes Agent 部署指南

本文档详细说明如何在本地或服务器上部署 Hermes Agent。

## 前置要求

### 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 10 GB | 50 GB+ |
| Docker | 20.10+ | 最新稳定版 |
| Docker Compose | 2.0+ | 最新稳定版 |

### 必需环境变量

```bash
# OpenAI API 配置
HERMES_API_KEY=sk-your-api-key-here
HERMES_MODEL=gpt-4

# 数据库密码
HERMES_DB_PASSWORD=your_secure_password

# 环境模式
HERMES_ENV=development
HERMES_LOG_LEVEL=INFO
```

## 快速部署

```bash
# 1. 进入部署目录
cd deploy/hermes

# 2. 创建 .env 文件
cat > .env << 'EOF'
HERMES_API_KEY=sk-your-api-key-here
HERMES_MODEL=gpt-4
HERMES_DB_PASSWORD=hermes_secure_password_123
HERMES_ENV=development
HERMES_LOG_LEVEL=INFO
EOF

# 3. 启动服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 验证健康状态
curl http://localhost:8080/health
```

## 环境变量完整列表

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| HERMES_ENV | 否 | development | 运行环境 |
| HERMES_LOG_LEVEL | 否 | INFO | 日志级别 |
| HERMES_MODEL | 是 | - | AI 模型名称 |
| HERMES_API_KEY | 是 | - | OpenAI API Key |
| HERMES_BASE_URL | 否 | OpenAI 默认 | API 基础 URL |
| HERMES_STORAGE_PATH | 否 | /app/hermes/data | 数据存储路径 |
| HERMES_SKILLS_PATH | 否 | /app/hermes/skills | 技能模块路径 |

## 常用操作

### 启动/停止服务

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务（保留数据）
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器和卷（清除数据）
docker-compose down -v
```

### 查看日志

```bash
# 查看 Hermes 日志
docker-compose logs -f hermes

# 查看所有服务日志
docker-compose logs -f
```

### 进入容器

```bash
# 进入 Hermes 容器
docker exec -it hermes-agent /bin/bash

# 进入 Redis
docker exec -it hermes-redis redis-cli

# 进入 PostgreSQL
docker exec -it hermes-postgres psql -U hermes -d hermes
```

### 备份数据

```bash
# 备份 PostgreSQL 数据
docker exec hermes-postgres pg_dump -U hermes hermes > backup_$(date +%Y%m%d).sql

# 备份 Redis 数据
docker exec hermes-redis redis-cli BGSAVE
docker cp hermes-redis:/data/dump.rdb ./redis_backup.rdb
```

## 故障排查

### 常见问题

#### 1. Hermes 服务启动失败

```bash
# 检查依赖服务是否运行
docker-compose ps

# 检查日志
docker-compose logs hermes --tail=50
```

#### 2. 无法连接数据库

```bash
# 检查 PostgreSQL
docker-compose ps postgres
docker exec -it hermes-postgres pg_isready -U hermes

# 重启 PostgreSQL
docker-compose restart postgres
```

#### 3. 端口冲突

修改 docker-compose.yml 中的端口映射，避免与本地服务冲突。

## 开发模式

```bash
# 启动开发模式（支持热重载）
docker-compose run --rm -p 8080:8080 hermes dev
```

## 生产部署注意事项

1. 安全配置
   - 使用强密码
   - 配置 HTTPS
   - 启用防火墙

2. 资源限制
   在 docker-compose.yml 中添加资源限制

3. 监控告警
   - 启用 Prometheus 监控
   - 配置日志收集
   - 设置资源告警

## 相关文档

- Hermes 项目主页: https://github.com/calcaware/hermes
- Archon 部署文档: ./archon.md

---

最后更新: 2026-04-13
