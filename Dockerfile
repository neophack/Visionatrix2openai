# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir uvicorn fastapi pydantic httpx

# 设置环境变量
ENV IMAGE_GENERATION_BASE_URL=http://172.16.134.251:8288
ENV IMAGE_GENERATION_MODEL=flux1_dev_8bit

# 暴露端口
EXPOSE 8000

# 运行命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
