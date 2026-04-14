#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$HOME/.hermes/skills/media/music"
BIN_DIR="$HOME/.local/bin"
BIN_PATH="$BIN_DIR/musicctl"

mkdir -p "$(dirname "$TARGET_DIR")"
rm -rf "$TARGET_DIR"
cp -R "$ROOT_DIR/skills/hermes/music" "$TARGET_DIR"

mkdir -p "$BIN_DIR"
cat > "$BIN_PATH" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$ROOT_DIR\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m musicctl.cli "\$@"
EOF
chmod +x "$BIN_PATH"

echo "Hermes music skill installed to: $TARGET_DIR"
echo "musicctl wrapper installed to: $BIN_PATH"
