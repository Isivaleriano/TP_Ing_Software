FROM python:3.13-slim

WORKDIR /app

COPY api/v1/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api /app/api

EXPOSE 8000

CMD ["uvicorn", "api.v1.main:app", "--host", "0.0.0.0", "--port", "8000"]