FROM python:3.11-alpine as dependencies_installer
WORKDIR /app

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


FROM python:3.11-alpine as runner

WORKDIR /app
ENV PYTHONPATH /app

COPY --from=dependencies_installer /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

EXPOSE 8000
ENTRYPOINT ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000"]
