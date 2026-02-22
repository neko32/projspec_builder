# Projspec Builder

コア指示モデルファイルを選択してプロジェクト情報を入力するだけで、プロジェクト仕様 Markdown を自動生成する TKinter GUI アプリです。

---

## 必要な環境

- Python 3.13 以上
- TKinter 8.6 以上（Python 標準ライブラリ）

---

## 事前準備

### 環境変数の設定

アプリ起動前に `CORE_DIRECTION_MODEL_DIR` 環境変数を設定してください。

**PowerShell:**
```powershell
$env:CORE_DIRECTION_MODEL_DIR = "C:\path\to\your\core-direction-files"
```

**bash / cmd:**
```bash
export CORE_DIRECTION_MODEL_DIR="C:/path/to/your/core-direction-files"
```

指定ディレクトリには `.md` 拡張子のコア指示モデルファイルが 1 つ以上必要です。

---

## 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

---

## 起動方法

### PowerShell
```powershell
.\scripts\start.ps1
```

### bash
```bash
bash scripts/start.sh
```

### 直接起動
```bash
python main.py
```

---

## 使い方

1. **Project Name** — プロジェクト名を入力（英数字・ハイフン・アンダースコア、3〜50文字）
2. **Project Root Directory** — Browse ボタンでプロジェクトのルートディレクトリを選択
3. **Core Direction File** — ドロップダウンからコア指示モデルを選択
4. **Output Directory** — Browse ボタンで出力先ディレクトリを選択
5. **Generate** ボタンを押すと `{Output Directory}/{Project Name}.md` が生成されます

---

## テスト実行

```bash
python -m pytest tests/
```

カバレッジレポートは `docs/coverage/index.html` に生成されます。

---

## 静的解析

```bash
python -m ruff check src/ tests/ main.py
```

---

## ドキュメント

| ファイル | 内容 |
|---|---|
| `docs/design.md` | 設計ドキュメント |
| `docs/api.md` | バックエンドロジック API 仕様 |
| `docs/dependencies.html` | 依存ライブラリ一覧 |
| `docs/coverage/` | コードカバレッジ HTML レポート |
