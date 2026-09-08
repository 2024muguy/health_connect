# HealthConnect AI - Deployment Guide

## Overview
This guide covers deployment of the HealthConnect AI Assistant using Docker Compose with Neon DB.

## Prerequisites
- Docker Desktop (or Docker Engine + Docker Compose)
- Neon DB account
- Pinecone account (for vector database)
- OpenAI API key (or Anthropic)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/healthconnect-ai.git
cd healthconnect-ai
2. Configure Environment Variables
bash
cp .env.example .env
nano .env
Fill in:

NEON_DATABASE_URL: Your Neon DB connection string

OPENAI_API_KEY: Your OpenAI API key

PINECONE_API_KEY: Your Pinecone API key

PINECONE_ENVIRONMENT: Your Pinecone environment

SECRET_KEY: Random secret key

3. Build and Start
bash
docker-compose build
docker-compose up -d
4. Verify Services
API: http://localhost:8000/health

Grafana: http://localhost:3000

Jupyter: http://localhost:8888

Prometheus: http://localhost:9090

Scaling
bash
# Scale app instances
docker-compose up -d --scale app=3

# Scale workers
docker-compose up -d --scale worker=2
Production Deployment
For production, use docker-compose.prod.yml:

bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
Cloud Deployment Options
Fly.io: fly launch

Railway: Connect GitHub repo

Google Cloud Run: Deploy container

Monitoring
Prometheus metrics: http://localhost:9090

Grafana dashboards: http://localhost:3000




