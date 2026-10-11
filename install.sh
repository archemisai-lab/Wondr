#!/data/data/com.termux/files/usr/bin/bash
set -e

PROJECT_DIR="$HOME/wondr"
VENV="$PROJECT_DIR/.venv"

echo ""
echo "  WONDR — Installation"
echo "  --------------------"

pkg install python git -y

if [ ! -f "$PROJECT_DIR/wondr.py" ]; then
    echo "Erreur : wondr.py est introuvable."
    exit 1
fi

if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "Configure ta clé API Gemini."
    read -r -s -p "Clé API : " API_KEY
    echo ""

    if [ -z "$API_KEY" ]; then
        echo "Aucune clé fournie. Installation annulée."
        exit 1
    fi

    printf 'GEMINI_API_KEY=%s\nGEMINI_MODEL=gemini-3.8-flash\n' \
        "$API_KEY" > "$PROJECT_DIR/.env"
    chmod 600 "$PROJECT_DIR/.env"
    unset API_KEY
fi

python -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

cat > "$PREFIX/bin/wondr" <<'LAUNCHER'
#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/wondr"
exec "$HOME/wondr/.venv/bin/python" "$HOME/wondr/wondr.py" "$@"
LAUNCHER

chmod +x "$PREFIX/bin/wondr"

echo ""
echo "Installation terminée."
echo "Lancement de Wondr..."
exec "$PREFIX/bin/wondr"
