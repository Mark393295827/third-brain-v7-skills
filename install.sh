#!/usr/bin/env bash
set -euo pipefail

REPO="Mark393295827/third-brain-v5-skills"
BRANCH="main"
SKILLS_DIR="$(dirname "$0")/skills"
ADAPTERS_DIR="$(dirname "$0")/adapters"
CONFIG_FILE="$(dirname "$0")/system/config.md"
TARGET_ARG="${1:-auto}"

echo "=== Third Brain V7 Skills Installer ==="
echo ""

# Detect agent harness
HARNESS=""
if [ "$TARGET_ARG" != "auto" ]; then
    HARNESS="$TARGET_ARG"
elif [ -n "$CLAUDE_CODE" ] || [ -d "$HOME/.claude" ]; then
    HARNESS="claude-code"
elif command -v codex &>/dev/null; then
    HARNESS="codex"
elif command -v gemini &>/dev/null; then
    HARNESS="gemini"
fi

# Determine install target
case "$HARNESS" in
    claude|claude-code)
        HARNESS="claude-code"
        TARGET="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
        echo "Detected: Claude Code"
        ;;
    codex)
        TARGET="$HOME/.agents/skills"
        echo "Detected: Codex CLI"
        ;;
    gemini)
        TARGET="$HOME/.gemini/skills"
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
        mkdir -p "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.gemini/skills" ".cursor/rules" ".windsurf/skills" ".windsurf/rules"
        cp -r "$SKILLS_DIR"/* "$HOME/.claude/skills/"
        cp -r "$SKILLS_DIR"/* "$HOME/.agents/skills/"
        cp -r "$SKILLS_DIR"/* "$HOME/.gemini/skills/"
        cp "$ADAPTERS_DIR/cursor/third-brain-skills.mdc" ".cursor/rules/third-brain-skills.mdc"
        cp -r "$SKILLS_DIR"/* ".windsurf/skills/"
        cp "$ADAPTERS_DIR/windsurf/third-brain-skills.md" ".windsurf/rules/third-brain-skills.md"
        echo "Installed all supported targets"
        exit 0
        ;;
    *)
        echo "No supported agent harness detected."
        echo "Installing to ~/.claude/skills/ by default..."
        HARNESS="claude-code"
        TARGET="$HOME/.claude/skills"
        ;;
esac

# Install
mkdir -p "$TARGET"
echo "Installing to: $TARGET"
if [ "$HARNESS" = "cursor" ]; then
    cp "$ADAPTERS_DIR/cursor/third-brain-skills.mdc" "$TARGET/third-brain-skills.mdc"
elif [ "$HARNESS" = "windsurf" ]; then
    cp -r "$SKILLS_DIR"/* "$TARGET/"
    mkdir -p ".windsurf/rules"
    cp "$ADAPTERS_DIR/windsurf/third-brain-skills.md" ".windsurf/rules/third-brain-skills.md"
else
    cp -r "$SKILLS_DIR"/* "$TARGET/"
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
