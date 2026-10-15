FROM python:3.12-slim
RUN pip install --no-cache-dir fastapi==0.119.0 uvicorn==0.37.0 requests==2.32.5
WORKDIR /app
COPY main.py .
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
