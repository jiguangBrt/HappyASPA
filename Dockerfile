FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
COPY . /app/
EXPOSE 5000
# 启动 Gunicorn 时，指定使用挂载进来的私钥和公钥
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "120", "--certfile=/app/ssl/dii.csuu.asia.pem", "--keyfile=/app/ssl/dii.csuu.asia.key", "app:create_app()"]