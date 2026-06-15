#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== RevRate - Automatyczna instalacja ==="
echo

REPO_URL="https://github.com/melzak252/SUML-CAR-PREDICTION.git"
REPO_BRANCH="deployment"
REPO_DIR="SUML-CAR-PREDICTION"

# === Zaleznosci systemowe ===
echo "Instalacja zaleznosci systemowych..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip git 2>/dev/null

# === Klonowanie repo ===
if [ -d "$REPO_DIR" ]; then
    echo "Repozytorium juz istnieje. Aktualizacja..."
    cd "$REPO_DIR"
    git pull
else
    echo "Klonowanie repozytorium..."
    git clone -b "$REPO_BRANCH" "$REPO_URL"
    cd "$REPO_DIR"
fi

# === venv ===
if [ ! -f ".venv/bin/python3" ]; then
    echo "=== Tworzenie srodowiska wirtualnego ==="
    python3 -m venv .venv
fi

echo ".venv gotowe."

# === Setup (instalacja zaleznosci + dataset + uruchomienie) ===
echo
echo "=== Uruchamianie setup ==="
bash scripts/linux/setup.sh