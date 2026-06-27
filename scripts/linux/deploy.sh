#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== RevRate - Automatyczna instalacja ==="
echo

ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m)"
case "$ARCH" in amd64|x86_64) PY_ARCH="x86_64" ;; arm64|aarch64) PY_ARCH="aarch64" ;; *) echo "Nieobsługiwana architektura: $ARCH"; exit 1 ;; esac

GIT_DIR="$SCRIPT_DIR/git"
PY_DIR="$SCRIPT_DIR/python3"

# === Git ===
echo "=== Pobieranie Git ==="
rm -rf "$GIT_DIR"
mkdir -p "$GIT_DIR"
TMPDIR="$(mktemp -d)"
apt-get download -qq git git-man 2>/dev/null || true
for deb in git_*.deb git-man_*.deb; do [ -f "$deb" ] && dpkg-deb -x "$deb" "$GIT_DIR/" 2>/dev/null; rm -f "$deb"; done
rm -rf "$TMPDIR"
if [ ! -x "$GIT_DIR/usr/bin/git" ]; then echo "Nie udalo sie pobrac Git."; exit 1; fi
export PATH="$GIT_DIR/usr/bin:$PATH"
export GIT_EXEC_PATH="$GIT_DIR/usr/lib/git-core"
echo "Git gotowy. $(git --version)"

# === Python ===
echo "=== Pobieranie Python3 ==="
rm -rf "$PY_DIR"
PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20260610/cpython-3.10.20%2B20260610-${PY_ARCH}-unknown-linux-gnu-install_only.tar.gz"
PY_TAR="/tmp/python3-standalone.tar.gz"
if command -v curl &>/dev/null; then curl -fSL "$PY_URL" -o "$PY_TAR"; else wget -q "$PY_URL" -O "$PY_TAR"; fi
if [ ! -s "$PY_TAR" ]; then echo "Nie udalo sie pobrac Pythona."; rm -f "$PY_TAR"; exit 1; fi
echo "Wypakowywanie Python..."
mkdir -p "$PY_DIR"
tar -xzf "$PY_TAR" -C "$PY_DIR"
rm -f "$PY_TAR"
PY_EXE="$PY_DIR/python/bin/python3"
if [ ! -x "$PY_EXE" ]; then echo "Nie udalo sie znalezc python3."; exit 1; fi
echo "Python gotowy. $($PY_EXE --version 2>&1)"

# === Klonowanie repo ===
REPO_URL="https://github.com/melzak252/SUML-CAR-PREDICTION.git"
PARENT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ -f "$PARENT_DIR/run.py" ]; then cd "$PARENT_DIR"; else git clone -b deployment "$REPO_URL" && cd SUML-CAR-PREDICTION; fi
REPO_ROOT="$(pwd)"

# === venv ===
echo "=== Tworzenie srodowiska wirtualnego ==="
"$PY_EXE" -m venv --copies "$REPO_ROOT/.venv" || { echo "Nie udalo sie utworzyc venv"; exit 1; }
echo "Kopiowanie bibliotek Pythona do venv..."
PY_VER=$("$REPO_ROOT/.venv/bin/python3" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
VENV_LIB="$REPO_ROOT/.venv/lib/python${PY_VER}"
STANDALONE_LIB="$PY_DIR/python/lib/python${PY_VER}"
if [ -d "$STANDALONE_LIB" ]; then
    mkdir -p "$VENV_LIB"
    for item in "$STANDALONE_LIB"/*; do [ "$(basename "$item")" = "site-packages" ] && continue; cp -rn "$item" "$VENV_LIB/" 2>/dev/null; done
    mkdir -p "$REPO_ROOT/.venv/lib"
    for lib in "$PY_DIR/python/lib/"libpython*.so*; do [ -f "$lib" ] && cp "$lib" "$REPO_ROOT/.venv/lib/" 2>/dev/null; done
fi
VENV_ABS="$(cd "$REPO_ROOT/.venv" && pwd)"
sed -i "s|^home = .*|home = ${VENV_ABS}/bin|" "$REPO_ROOT/.venv/pyvenv.cfg"

# === Instalacja zaleznosci ===
echo "=== Instalacja zaleznosci ==="
"$REPO_ROOT/.venv/bin/pip" install -r "$REPO_ROOT/requirements.txt" || { echo "Instalacja zaleznosci nieudana"; exit 1; }

# === Czyszczenie ===
echo "=== Czyszczenie tymczasowych plikow ==="
cd "$SCRIPT_DIR"
rm -rf "$GIT_DIR"; echo "Usunieto tymczasowy Git."
rm -rf "$PY_DIR"; echo "Usunieto tymczasowy Python."

cd "$REPO_ROOT"
echo "=== Uruchamianie setup ==="
bash scripts/linux/setup.sh