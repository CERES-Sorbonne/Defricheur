FROM python:3.12.6-alpine3.20

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN python ./src/init.py

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=4
ENV TIMEOUT=1000

EXPOSE 8000

CMD ["sh", "./run_docker.sh"]
