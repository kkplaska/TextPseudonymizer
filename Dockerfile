# Stage 1: Build Tailwind CSS
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY tailwind.config.js ./
COPY app/templates ./app/templates
COPY app/static/src ./app/static/src
RUN npm run build:css

# Stage 2: Build Python App
FROM python:3.11-slim
WORKDIR /usr/src/app

ARG APP_VERSION=v1.1.0
ARG GITHUB_REPO=https://github.com/kkplaska/TextPseudonymizer
ENV APP_VERSION=$APP_VERSION
ENV GITHUB_REPO=$GITHUB_REPO

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Copy compiled CSS from builder
COPY --from=builder /app/app/static/css /usr/src/app/app/static/css

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
