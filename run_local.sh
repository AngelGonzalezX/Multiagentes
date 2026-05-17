#!/bin/bash

echo "🚀 Iniciando todos los agentes..."

# Inicia cada agente en su propio puerto
GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2) \
uv run adk api_server agents/researcher --port 8001 &

GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2) \
uv run adk api_server agents/judge --port 8002 &

GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2) \
uv run adk api_server agents/content_builder --port 8003 &

sleep 3

echo "✅ Agentes corriendo en puertos 8001, 8002 y 8003"
echo "🎻 Iniciando Orchestrator en puerto 8004..."

RESEARCHER_AGENT_CARD_URL=http://localhost:8001/a2a/agent/.well-known/agent-card.json \
JUDGE_AGENT_CARD_URL=http://localhost:8002/a2a/agent/.well-known/agent-card.json \
CONTENT_BUILDER_AGENT_CARD_URL=http://localhost:8003/a2a/agent/.well-known/agent-card.json \
GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2) \
uv run adk api_server agents/orchestrator --port 8004