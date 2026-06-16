#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== RevRate - Automatyczna instalacja ==="
echo

REPO_URL="https://github.com/melzak252/SUML-CAR-PREDICTION/archive/refs/heads/deployment.tar.gz"
REPO_TGZ="$SCRIPT_DIR/repo.tar.gz"
REPO_DIR="SUML-CAR-PREDICTION"

PY_DIR="$SCRIPT_DIR/python3"
PY_EXE="$PY_DIR/bin/python3"
PY_URL="https://github.com/indygreg/python-build-standalone/releases/download/20230507/cpython-3.10.11+20230507-x86_64-unknown-linux-gnu-install_only.tar.gz"
PY_TGZ="$SCRIPT_DIR/python-portable.tar.gz"
LOCAL_PY_TGZ="$SCRIPT_DIR/cpython-3.10.11-linux.tar.gz"

# === Python ===
if [ ! -f "$PY_EXE" ]; then
    if [ -f "$LOCAL_PY_TGZ" ]; then
        echo "Znaleziono lokalny plik Pythona."
        PY_TGZ="$LOCAL_PY_TGZ"
    else
        echo "Pobieranie Python 3.10 (portable)..."
        if ! curl -fSL --connect-timeout 30 -o "$PY_TGZ" "$PY_URL"; then
            echo
            echo "Nie udalo sie pobrac Pythona z sieci."
            echo "Pobierz recznie z:"
            echo "  https://github.com/indygreg/python-build-standalone/releases"
            echo "  (cpython-3.10.11+20230507-x86_64-unknown-linux-gnu-install_only.tar.gz)"
            echo "i umiesc jako $LOCAL_PY_TGZ, potem uruchom ponownie."
            exit 1
        fi
    fi

    echo "Wypakowywanie Python..."
    mkdir -p "$PY_DIR"
    tar -xzf "$PY_TGZ" -C "$PY_DIR" --strip-components=1
    rm -f "$PY_TGZ"
fi
echo "Python gotowy: $("$PY_EXE" --version 2>&1)"

# === Repozytorium (pobierane jako tarball, git nie jest potrzebny) ===
if [ -d "$REPO_DIR" ]; then
    echo "Repozytorium juz istnieje. Usuwanie starej kopii..."
    rm -rf "$REPO_DIR"
fi

echo "Pobieranie repozytorium..."
if ! curl -fSL --connect-timeout 30 -o "$REPO_TGZ" "$REPO_URL"; then
    echo
    echo "Nie udalo sie pobrac repozytorium z GitHuba."
    echo "Sprawdz polaczenie internetowe i sprobuj ponownie."
    exit 1
fi

echo "Wypakowywanie repozytorium..."
mkdir -p "$REPO_DIR"
tar -xzf "$REPO_TGZ" -C "$REPO_DIR" --strip-components=1
rm -f "$REPO_TGZ"
cd "$REPO_DIR"

# === venv (samodzielne, niezalezne od portable Pythona) ===
if [ ! -f ".venv/bin/python3" ]; then
    echo "=== Tworzenie srodowiska wirtualnego ==="
    "$PY_EXE" -m venv --copies .venv

    echo "Kopiowanie bibliotek do venv..."
    cp -rf "$PY_DIR/lib/"* ".venv/lib/" 2>/dev/null || true

    echo "Aktualizacja konfiguracji venv..."
    VENV_BIN="$(cd .venv/bin && pwd)"
    if [ -f ".venv/pyvenv.cfg" ]; then
        sed -i "s|^home = .*|home = $VENV_BIN|" .venv/pyvenv.cfg
    fi
fi
echo ".venv gotowe."

# === Instalacja zaleznosci ===
source .venv/bin/activate
echo
echo "=== Instalacja zaleznosci ==="
pip install -r requirements.txt
deactivate

# === Czyszczenie tymczasowego Pythona ===
echo
echo "=== Czyszczenie tymczasowych plikow ==="
cd "$SCRIPT_DIR"
if [ -d "python3" ]; then
    echo "Usuwanie tymczasowego Python..."
    rm -rf "python3"
fi
cd "$SCRIPT_DIR/$REPO_DIR"

# === Setup (rozpakowanie datasetu + uruchomienie) ===
echo
echo "=== Uruchamianie setup ==="
bash scripts/linux/setup.sh
