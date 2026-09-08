# HealthConnect AI Assistant

## Overview
HealthConnect AI Assistant is a production-grade conversational AI system designed to reduce appointment no-shows and improve patient support for HealthConnect Clinic. The system leverages Retrieval-Augmented Generation (RAG), multi-agent orchestration, and MCP tool integration to provide safe, accurate, and helpful administrative support.

## Features
- **Multi-Agent System**: 10 specialized agents for intent routing, conversation, safety, and analytics
- **RAG Pipeline**: Document ingestion, chunking, embedding, and retrieval with hybrid search
- **Safety Framework**: Defense-in-depth safety with pre/post-generation checks
- **MCP Integration**: 6 MCP servers for database, calendar, email, knowledge base, analytics, and notifications
- **Human-in-the-Loop**: Escalation workflows for critical actions
- **Monitoring**: Prometheus metrics, Grafana dashboards, structured logging
- **Model Training**: Jupyter notebooks for intent classification, safety classification, and embedding fine-tuning

## Architecture
┌─────────────────────────────────────────────────────────────────────────┐
│ HEALTHCONNECT AI ASSISTANT │
│ SYSTEM ARCHITECTURE │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ USER LAYER │
│ ┌───────────┐ │
│ │ Patient │ │
│ │ Web/Mobile│ │
│ └─────┬─────┘ │
└────────┼────────┘
│ HTTPS
┌────────┼────────────────────────────────────────────────────────┐
│ API GATEWAY LAYER │
│ ┌─────┴─────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ Auth │ │ Rate │ │ Request │ │ Load │ │
│ │ (JWT) │ │ Limiting │ │ Validation│ │ Balancing│ │
│ └───────────┘ └──────────┘ └──────────┘ └──────────┘ │
└──────────────────────────────────────────────────────────────────┘
│
┌────────┼────────────────────────────────────────────────────────┐
│ APPLICATION LAYER (FastAPI) │
│ ┌─────┴──────────────────────────────────────────────┐ │
│ │ ORCHESTRATOR │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│ │ │ Intent │→│ Safety │→│ RAG │ │ │
│ │ │ Router │ │ Check │ │ Pipeline │ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
│
┌────────┼────────────────────────────────────────────────────────┐
│ AI LAYER │
│ ┌─────┴──────────────────────────────────────────────┐ │
│ │ MULTI-AGENT SYSTEM │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│ │ │Conversation│ │Knowledge │ │ Safety │ │ │
│ │ │ Agent │ │ Agent │ │ Agent │ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│ │ │ Action │ │ Summary │ │Analytics │ │ │
│ │ │ Agent │ │ Agent │ │ Agent │ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ RAG PIPELINE │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ │ │
│ │ │Document │→│Chunking │→│Embedding │→│Vector │ │ │
│ │ │Ingestion │ │Engine │ │Engine │ │Store │ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ └───────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
│
┌────────┼────────────────────────────────────────────────────────┐
│ MCP TOOL LAYER │
│ ┌─────┴──────────────────────────────────────────────┐ │
│ │ MCP SERVERS │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│ │ │Database │ │Calendar │ │Email │ │ │
│ │ │Tools │ │Tools │ │Tools │ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│ │ │Knowledge │ │Analytics │ │Notification│ │ │
│ │ │Base Tools│ │Tools │ │Tools │ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
│
┌────────┼────────────────────────────────────────────────────────┐
│ DATA LAYER │
│ ┌─────┴──────────────────────────────────────────────┐ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ │ │
│ │ │Neon DB │ │Redis │ │Pinecone │ │S3 │ │ │
│ │ │PostgreSQL│ │Cache │ │Vector DB │ │Storage│ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ └───────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘


## Quick Start

### Prerequisites
- Docker Desktop
- Neon DB account
- Pinecone account
- OpenAI API key

### Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/healthconnect-ai.git
cd healthconnect-ai

# 2. Copy environment variables
cp .env.example .env

# 3. Edit .env with your credentials
nano .env

# 4. Start services
docker-compose up -d

# 5. Access services
# API: http://localhost:8000
# Grafana: http://localhost:3000
# Jupyter: http://localhost:8888
Project Structure
See Architecture_Overview.md for detailed structure.

Documentation
API Documentation

Deployment Guide

Model Training Guide

Evaluation Report

License
MIT