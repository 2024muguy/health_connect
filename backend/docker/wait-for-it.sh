#!/bin/bash
# ============================================
# HealthConnect AI - Wait for Service Script
# ============================================
# Usage: wait-for-it.sh host:port [-t timeout] [-- command args]
# ============================================

TIMEOUT=30
QUIET=0
HOST=""
PORT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        *:* )
            HOST=$(echo "$1" | cut -d: -f1)
            PORT=$(echo "$1" | cut -d: -f2)
            shift
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -q|--quiet)
            QUIET=1
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            break
            ;;
    esac
done

if [ -z "$HOST" ] || [ -z "$PORT" ]; then
    echo "Usage: wait-for-it.sh host:port [-t timeout] [-q] [-- command args]"
    exit 1
fi

# Function to check if service is available
check_service() {
    (echo > /dev/tcp/$HOST/$PORT) >/dev/null 2>&1
    return $?
}

# Wait for service
echo "Waiting for $HOST:$PORT (timeout: ${TIMEOUT}s)..."

START_TIME=$(date +%s)

while ! check_service; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "✗ Timeout after ${TIMEOUT}s waiting for $HOST:$PORT"
        exit 1
    fi
    
    if [ $QUIET -eq 0 ]; then
        echo "  Waiting for $HOST:$PORT (${ELAPSED}s elapsed)..."
    fi
    
    sleep 1
done

echo "✓ $HOST:$PORT is available"

# Execute command if provided
if [ $# -gt 0 ]; then
    exec "$@"
fi