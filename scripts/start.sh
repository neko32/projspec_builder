#!/usr/bin/env bash
# Projspec Builder 起動スクリプト (bash)
# プロジェクトルートから実行してください: bash scripts/start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
python main.py
