#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
VENV_DIR=".m02_venv"
REQ_FILE="requirements.txt"

# --- Checks ---
if [[ ! -f "$REQ_FILE" ]]; then
  echo "❌ No se encontró $REQ_FILE en $(pwd)"
  exit 1
fi

# --- Create venv if missing ---
if [[ ! -d "$VENV_DIR" ]]; then
  echo "🔧 Creando entorno virtual en $VENV_DIR ..."
  python3 -m venv $VENV_DIR
else
  echo "✅ Entorno virtual ya existe: $VENV_DIR"
fi

# --- Activate ---
# shellcheck disable=SC1090
source $VENV_DIR/bin/activate

# --- Upgrade pip ---
echo "⬆️  Actualizando pip..."
python -m pip install --upgrade pip

# --- Install deps (only when needed) ---
# Tip: instala siempre; pip es inteligente y no reinstala lo mismo.
echo "📦 Instalando dependencias desde $REQ_FILE ..."
pip install -r $REQ_FILE

# --- Ensure kernel for Jupyter (nice to have) ---
echo "🧠 Registrando kernel de Jupyter (si aplica)..."
python -m ipykernel install --user --name "$(basename "$(pwd)")" --display-name "Python ($(basename "$(pwd)"))" >/dev/null 2>&1 || true

# --- Run Jupyter ---
echo "🚀 Iniciando Jupyter Lab..."
jupyter lab