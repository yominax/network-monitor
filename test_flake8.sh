#!/bin/bash
# Script pour tester flake8 exactement comme dans le CI

echo "Test flake8 (comme dans GitHub Actions)..."
echo ""

# Active le venv si disponible
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Installe flake8 si pas déjà installé
if ! command -v flake8 &> /dev/null; then
    echo "Installation de flake8..."
    pip install flake8
fi

# Lance flake8 exactement comme dans le CI
echo "Lancement de flake8 network_monitor tests"
flake8 network_monitor tests

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ flake8: Aucune erreur !"
    exit 0
else
    echo ""
    echo "❌ flake8: Erreurs détectées (code: $EXIT_CODE)"
    exit $EXIT_CODE
fi
