#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(dirname "$0")/skills"
ADAPTERS_DIR="$(dirname "$0")/adapters"
CONFIG_FILE="$(dirname "$0")/system/config.md"
INSTALL_HELPER="$(dirname "$0")/tools/install_skills.py"
TARGET_ARG="${1:-auto}"
INSTALL_HOME="${THIRD_BRAIN_HOME:-$HOME}"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Python 3 is required for manifest-driven installation." >&2
    exit 2
fi

copy_skills() {
    local destination="$1"
    "$PYTHON_BIN" "$INSTALL_HELPER" --source "$SKILLS_DIR" --destination "$destination"
}

echo "=== Third Brain V8.1 Skills Installer ==="
echo ""

# Detect agent harness
HARNESS=""
if [ "$TARGET_ARG" != "auto" ]; then
    HARNESS="$TARGET_ARG"
elif command -v codex &>/dev/null || [ -d "$INSTALL_HOME/.agents" ]; then
    HARNESS="codex"
elif [ -n "${CLAUDE_CODE:-}" ] || [ -d "$INSTALL_HOME/.claude" ]; then
    HARNESS="claude-code"
elif command -v gemini &>/dev/null; then
    HARNESS="gemini"
fi

# Determine install target
case "$HARNESS" in
    claude|claude-code)
        HARNESS="claude-code"
        TARGET="${CLAUDE_SKILLS_DIR:-$INSTALL_HOME/.claude/skills}"
        echo "Detected: Claude Code"
        ;;
    codex)
        TARGET="$INSTALL_HOME/.agents/skills"
        echo "Detected: Codex CLI"
        ;;
    gemini)
        TARGET="$INSTALL_HOME/.gemini/skills"
        echo "Detected: Gemini CLI"
        ;;
    cursor)
        TARGET=".cursor/rules"
        echo "Target: Cursor rules adapter"
        ;;
    windsurf)
        TARGET=".windsurf/skills"
        echo "Target: Windsurf workspace skills"
        ;;
    all)
        echo "Installing all supported local targets..."
        mkdir -p "$INSTALL_HOME/.claude/skills" "$INSTALL_HOME/.agents/skills" "$INSTALL_HOME/.gemini/skills" ".cursor/rules" ".windsurf/skills" ".windsurf/rules"
        copy_skills "$INSTALL_HOME/.claude/skills"
        copy_skills "$INSTALL_HOME/.agents/skills"
        copy_skills "$INSTALL_HOME/.gemini/skills"
        cp "$ADAPTERS_DIR/cursor/third-brain-skills.mdc" ".cursor/rules/third-brain-skills.mdc"
        copy_skills ".windsurf/skills"
        cp "$ADAPTERS_DIR/windsurf/third-brain-skills.md" ".windsurf/rules/third-brain-skills.md"
        echo "Installed all supported targets"
        exit 0
        ;;
    bundle|agentic-os)
        BUNDLE_DIR="${THIRD_BRAIN_BUNDLE_DIR:-$INSTALL_HOME/.third-brain/bundles}"
        mkdir -p "$BUNDLE_DIR"
        OUTPUT="$BUNDLE_DIR/third-brain-agentic-os-v8.1.zip"
        "$PYTHON_BIN" "$(dirname "$0")/tools/package_agentic_os.py" --output "$OUTPUT"
        "$PYTHON_BIN" "$(dirname "$0")/tools/package_agentic_os.py" --verify "$OUTPUT"
        echo "Created Codex Agentic OS bundle: $OUTPUT"
        exit 0
        ;;
    *)
        echo "No supported agent harness detected."
        echo "Installing to ~/.agents/skills/ (Codex primary; use an explicit target for compatibility adapters)..."
        HARNESS="codex"
        TARGET="$INSTALL_HOME/.agents/skills"
        ;;
esac

# Install
mkdir -p "$TARGET"
echo "Installing to: $TARGET"
if [ "$HARNESS" = "cursor" ]; then
    cp "$ADAPTERS_DIR/cursor/third-brain-skills.mdc" "$TARGET/third-brain-skills.mdc"
elif [ "$HARNESS" = "windsurf" ]; then
    copy_skills "$TARGET"
    mkdir -p ".windsurf/rules"
    cp "$ADAPTERS_DIR/windsurf/third-brain-skills.md" ".windsurf/rules/third-brain-skills.md"
else
    copy_skills "$TARGET"
fi
echo ""
if [ "$HARNESS" = "cursor" ]; then
    echo "✅ Installed Cursor rules adapter"
else
    echo "✅ Installed $(ls -d "$SKILLS_DIR"/*/ | wc -l) skills"
fi
echo ""
echo "Available skills:"
for skill in "$SKILLS_DIR"/*/; do
    name=$(basename "$skill")
    desc=$(head -5 "$skill/SKILL.md" 2>/dev/null | grep "^description:" | sed 's/^description: //')
    echo "  - $name${desc:+: $desc}"
done

echo ""
if [ -f "$CONFIG_FILE" ]; then
    echo "Path config template: $CONFIG_FILE"
    echo "Copy it into your vault as system/config.md if your wiki folders differ from the defaults."
fi
