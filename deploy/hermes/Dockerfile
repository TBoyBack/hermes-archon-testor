# Hermes Agent Docker Image
# 基于 Python 3.11 和 Docker in Docker 支持

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖和 Docker CLI
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV HERMES_VERSION=1.0.0
ENV HERMES_HOME=/app/hermes
ENV PYTHONUNBUFFERED=1

# 复制应用文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建 Hermes 工作目录
RUN mkdir -p ${HERMES_HOME}/{skills,logs,data,cache}

# 复制 Hermes 核心模块
COPY src/hermes/ ${HERMES_HOME}/src/hermes/

# 设置入口脚本
COPY deploy/hermes/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 暴露端口
EXPOSE 8080 8081

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["hermes", "start"]
