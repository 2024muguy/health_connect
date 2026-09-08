#!/bin/bash
# ============================================
# HealthConnect AI - Entrypoint Script
# ============================================
set -e

echo "=========================================="
echo "HealthConnect AI Assistant"
echo "=========================================="
echo "Environment: ${ENVIRONMENT:-development}"
echo "App Version: ${APP_VERSION:-1.0.0}"
echo "=========================================="

# Function to wait for service availability
wait_for_service() {
    local host="$1"
    local port="$2"
    local service_name="$3"
    local max_attempts="${4:-30}"
    local attempt=1

    echo "Waiting for ${service_name} at ${host}:${port}..."
    
    while ! nc -z "$host" "$port" 2>/dev/null; do
        if [ $attempt -ge $max_attempts ]; then
            echo "ERROR: ${service_name} not available after ${max_attempts} attempts"
            exit 1
        fi
        echo "  Attempt ${attempt}/${max_attempts}: ${service_name} not ready, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "✓ ${service_name} is available"
}

# Wait for Redis
if [ -n "$REDIS_URL" ]; then
    # Extract host and port from Redis URL
    REDIS_HOST=$(echo "$REDIS_URL" | sed -E 's/redis:\/\/([^:]+):([0-9]+).*/\1/')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -E 's/redis:\/\/([^:]+):([0-9]+).*/\2/')
    
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
    fi
fi

# Run database migrations (if applicable)
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
    echo "✓ Migrations complete"
fi

# Ingest knowledge base (if requested)
if [ "${INGEST_KB:-false}" = "true" ]; then
    echo "Ingesting knowledge base..."
    python scripts/ingest_knowledge_base.py
    echo "✓ Knowledge base ingestion complete"
fi

echo "=========================================="
echo "Starting application..."
echo "=========================================="

# Execute the main command
exec "$@"