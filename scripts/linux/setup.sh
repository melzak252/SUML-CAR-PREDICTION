#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== RevRate ==="
echo

if [ ! -f ".venv/bin/python3" ]; then
    echo ".venv nie istnieje. Uruchom deploy.sh najpierw."
    exit 1
fi

source .venv/bin/activate

echo "=== Instalacja zaleznosci ==="
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Instalacja zaleznosci nieudana"
    exit 1
fi

echo
echo "=== Wypakowywanie datasetu ==="
python backend/tools/unpack_dataset.py || echo "Nie udalo sie wypakowac datasetu."

echo
echo "=== Uruchamianie ==="
python run.py