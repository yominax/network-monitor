#!/bin/bash
# Script de test pour vérifier que tout fonctionne

echo "=== Test 1: Vérifier que le runner Python expose les métriques ==="
curl -s http://localhost:8000/metrics | head -20
if [ $? -eq 0 ]; then
    echo "✓ Les métriques sont accessibles sur localhost:8000"
else
    echo "✗ ERREUR: Le runner Python ne tourne pas ou n'est pas accessible"
    echo "  Lance: python -m network_monitor.runner --config targets.yaml --interval 5"
fi

echo ""
echo "=== Test 2: Vérifier que Prometheus est accessible ==="
curl -s http://localhost:9090/-/healthy
if [ $? -eq 0 ]; then
    echo "✓ Prometheus est accessible sur localhost:9090"
else
    echo "✗ ERREUR: Prometheus n'est pas accessible"
    echo "  Lance: docker compose up"
fi

echo ""
echo "=== Test 3: Vérifier que Prometheus peut scraper les métriques ==="
curl -s "http://localhost:9090/api/v1/targets" | grep -q "UP"
if [ $? -eq 0 ]; then
    echo "✓ Prometheus peut scraper les métriques (target UP)"
else
    echo "✗ ERREUR: Prometheus ne peut pas scraper les métriques"
    echo "  Vérifie: http://localhost:9090/targets"
fi

echo ""
echo "=== Test 4: Vérifier que Grafana est accessible ==="
curl -s http://localhost:3000/api/health
if [ $? -eq 0 ]; then
    echo "✓ Grafana est accessible sur localhost:3000"
else
    echo "✗ ERREUR: Grafana n'est pas accessible"
    echo "  Lance: docker compose up"
fi
