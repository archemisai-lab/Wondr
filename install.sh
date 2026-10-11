#!/data/data/com.termux/files/usr/bin/bash
set -e

REPO_URL="https://github.com/archemisai-lab/Wondr.git"
PROJECT_DIR="$HOME/wondr-app"
VENV="$PROJECT_DIR/.venv"

echo ""
echo "WONDR - Installation"
pkg install -y python git

if [ -d "$PROJECT_DIR/.git" ]; then
    git -C "$PROJECT_DIR" pull --ff-only
elif [ -e "$PROJECT_DIR" ]; then
    echo "Erreur : le dossier $PROJECT_DIR existe déjà."
    exit 1
else
    git clone "$REPO_URL" "$PROJECT_DIR"
fi

if [ ! -f "$PROJECT_DIR/wondr.py" ]; then
    echo "Erreur : wondr.py est introuvable."
    exit 1
fi

if [ ! -f "$PROJECT_DIR/.env" ]; then
    printf "Clé API Gemini : "
    read -r -s API_KEY </dev/tty
    echo ""
    if [ -z "$API_KEY" ]; then
        echo "Clé API manquante."
        exit 1
    fi
    printf 'GEMINI_API_KEY=%s\nGEMINI_MODEL=gemini-3.8-flash\n' "$API_KEY" > "$PROJECT_DIR/.env"
    chmod 600 "$PROJECT_DIR/.env"
    unset API_KEY
fi

python -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

cat > "$PREFIX/bin/wondr" <<'LAUNCHER'
#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/wondr-app"
exec "$HOME/wondr-app/.venv/bin/python" "$HOME/wondr-app/wondr.py" "$@"
LAUNCHER

chmod +x "$PREFIX/bin/wondr"

echo "Installation terminée."
exec "$PREFIX/bin/wondr"
