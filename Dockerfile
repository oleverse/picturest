FROM python:3.10.12-slim

RUN useradd -m picturest
WORKDIR /home/picturest
COPY .env pyproject.toml README.md LICENSE .
COPY . $WORKDIR
RUN chown -R picturest:picturest /home/picturest
RUN chmod 0400 key.pem
USER picturest

ENV PATH="$PATH:/home/picturest/.local/bin"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -r requirements.txt


ENTRYPOINT ["python", "main.py"]
#ENTRYPOINT uvicorn main:app --host 0.0.0.0 --ssl-keyfile=key.pem --ssl-certfile=cert.pem

CMD alembic upgrade head

