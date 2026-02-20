#!/bin/bash
# Script pour tester localement ce que fait le CI/CD
# Lance ce script avant de pousser sur GitHub pour vérifier que tout passera

echo "=========================================="
echo "Test CI/CD local - Network Monitor"
echo "=========================================="
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Test 1: Vérifier que Python est installé
echo "1. Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python installé: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python n'est pas installé"
    ERRORS=$((ERRORS + 1))
fi

# Test 2: Vérifier que Doxygen est installé
echo ""
echo "2. Vérification de Doxygen..."
if command -v doxygen &> /dev/null; then
    DOXYGEN_VERSION=$(doxygen --version)
    echo -e "${GREEN}✓${NC} Doxygen installé: $DOXYGEN_VERSION"
else
    echo -e "${RED}✗${NC} Doxygen n'est pas installé"
    echo "   Installe avec: sudo apt install -y doxygen graphviz"
    ERRORS=$((ERRORS + 1))
fi

# Test 3: Vérifier que flake8 est installé
echo ""
echo "3. Vérification de flake8..."
if command -v flake8 &> /dev/null; then
    echo -e "${GREEN}✓${NC} flake8 installé"
else
    echo -e "${YELLOW}⚠${NC} flake8 n'est pas installé"
    echo "   Installe avec: pip install flake8"
    echo "   Ou active ton venv: source .venv/bin/activate"
fi

# Test 4: Vérifier que pytest est installé
echo ""
echo "4. Vérification de pytest..."
if command -v pytest &> /dev/null; then
    echo -e "${GREEN}✓${NC} pytest installé"
else
    echo -e "${YELLOW}⚠${NC} pytest n'est pas installé"
    echo "   Installe avec: pip install pytest"
    echo "   Ou active ton venv: source .venv/bin/activate"
fi

# Test 5: Installer les dépendances Python (si venv existe)
echo ""
echo "5. Installation des dépendances Python..."
if [ -d ".venv" ]; then
    echo "   Activation du venv..."
    source .venv/bin/activate
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Dépendances installées"
else
    echo -e "${YELLOW}⚠${NC} Pas de venv trouvé, installe manuellement: pip install -r requirements.txt"
fi

# Test 6: Lint avec flake8
echo ""
echo "6. Lint avec flake8..."
if command -v flake8 &> /dev/null; then
    if flake8 network_monitor tests 2>&1; then
        echo -e "${GREEN}✓${NC} flake8: Aucune erreur de style"
    else
        echo -e "${RED}✗${NC} flake8: Erreurs de style détectées"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} flake8 non disponible, skip"
fi

# Test 7: Tests avec pytest
echo ""
echo "7. Tests avec pytest..."
if command -v pytest &> /dev/null; then
    if pytest -q 2>&1; then
        echo -e "${GREEN}✓${NC} pytest: Tous les tests passent"
    else
        echo -e "${RED}✗${NC} pytest: Des tests échouent"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} pytest non disponible, skip"
fi

# Test 8: Génération de la documentation avec Doxygen
echo ""
echo "8. Génération de la documentation avec Doxygen..."
if command -v doxygen &> /dev/null; then
    if doxygen Doxyfile 2>&1 | grep -q "error"; then
        echo -e "${RED}✗${NC} Doxygen: Erreurs lors de la génération"
        doxygen Doxyfile 2>&1 | grep "error"
        ERRORS=$((ERRORS + 1))
    else
        if [ -f "docs/html/index.html" ]; then
            echo -e "${GREEN}✓${NC} Doxygen: Documentation générée dans docs/html/"
        else
            echo -e "${RED}✗${NC} Doxygen: Fichier index.html non trouvé"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Doxygen non disponible, skip"
fi

# Résumé
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les tests passent !${NC}"
    echo "   Tu peux pousser sur GitHub avec confiance."
else
    echo -e "${RED}❌ $ERRORS erreur(s) détectée(s)${NC}"
    echo "   Corrige les erreurs avant de pousser sur GitHub."
fi
echo "=========================================="

exit $ERRORS
