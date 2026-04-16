# backend/Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，确保 Python 输出直接刷新到终端
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- 优化点：切换到腾讯云镜像源 ---
RUN sed -i 's/deb.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/security.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list

# 安装系统依赖 (MySQL 编译需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装项目依赖 (设置全局镜像源，防止强制更新 pip 时超时)
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 拷贝项目代码
COPY backend/ .

# 暴露端口 (云托管通常探测 80 端口)
EXPOSE 80

# 启动命令 (指定 80 端口)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
