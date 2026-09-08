#!/bin/bash
# ============================================
# HealthConnect AI - Health Check Script
# ============================================

# Check if application is healthy
check_health() {
    local url="${1:-http://localhost:8000/health}"
    local max_attempts="${2:-5}"
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✓ Health check passed"
            return 0
        fi
        
        echo "✗ Health check failed (attempt ${attempt}/${max_attempts})"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "✗ Health check failed after ${max_attempts} attempts"
    return 1
}

# Check Redis
check_redis() {
    if redis-cli ping > /dev/null 2>&1; then
        echo "✓ Redis is healthy"
        return 0
    else
        echo "✗ Redis is unhealthy"
        return 1
    fi
}

# Check Database
check_database() {
    if [ -n "$NEON_DATABASE_URL" ]; then
        if python -c "from sqlalchemy import create_engine; engine = create_engine('$NEON_DATABASE_URL'); conn = engine.connect(); conn.close(); print('✓ Database is healthy')" 2>/dev/null; then
            return 0
        else
            echo "✗ Database is unhealthy"
            return 1
        fi
    fi
}

# Main
main() {
    echo "=========================================="
    echo "Health Check - HealthConnect AI"
    echo "=========================================="
    
    check_health
    check_redis
    check_database
    
    echo "=========================================="
}

main