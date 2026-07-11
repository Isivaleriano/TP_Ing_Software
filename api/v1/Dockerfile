FROM python:3.13-slim

WORKDIR /app

COPY api/v1/requirements.txt /tmp/api-requirements.txt
COPY ml/requirements.txt /tmp/ml-requirements.txt

RUN pip install --no-cache-dir \
    -r /tmp/api-requirements.txt \
    -r /tmp/ml-requirements.txt

COPY api /app/api
COPY ml /app/ml

EXPOSE 8000

CMD ["uvicorn", "api.v1.main:app", "--host", "0.0.0.0", "--port", "8000"]