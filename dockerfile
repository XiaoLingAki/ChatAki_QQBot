# 使用一个Python基础映像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制所有文件到工作目录
COPY . /app

# 运行pip安装依赖
RUN pip install -r requirements.txt

# 执行Python应用程序
CMD ["python", "api.py"]
