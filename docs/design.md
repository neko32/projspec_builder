# Projspec Builder 設計ドキュメント

## 概要

`projspec_builder` は TKinter ベースのシンプルな Python GUI アプリケーションです。
コア指示モデルファイル（.md）を選択してプロジェクト情報を入力後、Generate ボタンを押すと
指定された出力ディレクトリにプロジェクト仕様 Markdown ファイルを生成します。

---

## アーキテクチャ

```
projspec_builder/
├── assets/                   # アイコン、画像など（アイコンは外部パス参照）
├── data/
│   └── settings.json         # アプリ設定（バージョン情報など）
├── docs/                     # 設計ドキュメント・カバレッジレポート
│   ├── design.md             # 本ドキュメント
│   ├── api.md                # バックエンドロジックAPI仕様
│   ├── dependencies.html     # 依存ライブラリ一覧
│   └── coverage/             # pytest-cov HTMLレポート
├── scripts/
│   ├── start.ps1             # PowerShell 起動スクリプト
│   └── start.sh              # Bash 起動スクリプト
├── src/
│   ├── __init__.py
│   ├── app.py                # メインアプリケーションクラス (TKinter)
│   ├── components/
│   │   ├── __init__.py
│   │   └── progress_dialog.py  # モーダル進捗ダイアログ
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py        # 環境チェック・ファイル生成ロジック
│       └── validators.py     # Pydantic バリデーションモデル
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # セッション共有フィクスチャ
│   ├── test_app.py
│   ├── test_helpers.py
│   ├── test_progress_dialog.py
│   └── test_validators.py
├── main.py                   # エントリーポイント
├── pyproject.toml            # ruff・pytest 設定
└── requirements.txt          # 依存ライブラリ一覧
```

---

## 主要コンポーネント

### `src/app.py` — ProjspecBuilderApp

TKinter メインウィンドウを管理するクラスです。

| 責務 | 概要 |
|---|---|
| 起動チェック | `check_environment()` を呼び出し、エラー時はメッセージを表示してアプリを終了 |
| フォーム描画 | 4つの入力フィールド + 2つのボタンをシングルページに配置 |
| バリデーション | `ProjectFormData` (Pydantic) でフォーム全体を検証 |
| Generate 処理 | バックグラウンドスレッドでファイル生成、`ProgressDialog` を表示 |
| Clear 処理 | 確認ダイアログ後にフォームを初期値へリセット |

**ウィンドウ仕様:**
- サイズ: 1100 × 620 px（固定）
- コンテンツ領域: 左右 100px パディング（実質 900px）
- ベースカラー: `#7297c5`、セカンダリーカラー: `#666666`

### `src/utils/helpers.py` — ヘルパー関数群

UIに依存しない純粋なロジック関数で、すべてモック可能です。

| 関数 | 概要 |
|---|---|
| `check_environment()` | `CORE_DIRECTION_MODEL_DIR` 環境変数を検証し、有効なパスを返す |
| `get_core_direction_files(directory)` | 指定ディレクトリの `.md` ファイル名一覧をソート順で返す |
| `check_output_exists(output_dir, project_name)` | 出力ファイルの重複チェック |
| `generate_file(...)` | テンプレートを読み込み、プレースホルダーを置換し、出力ファイルを書き出す |

### `src/utils/validators.py` — Pydantic モデル

`ProjectFormData` で全フォーム入力を一括バリデーションします。

| フィールド | 制約 |
|---|---|
| `project_name` | 3〜50文字、英数字・ハイフン・アンダースコアのみ |
| `project_root_dir` | str（空文字は許可しない） |
| `core_direction_file` | str |
| `output_dir` | str |

### `src/components/progress_dialog.py` — ProgressDialog

`tk.Toplevel` を継承したモーダルダイアログです。

- `after()` ポーリング（100ms 間隔）でバックグラウンドスレッドの完了を監視
- 完了後: 成功/失敗の `messagebox` を表示して `destroy()`
- ユーザーが閉じた場合: `cancel_event.set()` でスレッドをキャンセル

---

## ファイル生成ロジック

```
{CORE_DIRECTION_MODEL_DIR}/{選択ファイル名}
    ↓ read (UTF-8, CP932 フォールバック)
テンプレート文字列
    ↓ replace("{{project_name}}", ...)
    ↓ replace("{{project_root_dir}}", ...)
    ↓ cancel_event チェック
{output_dir}/{project_name}.md に write (UTF-8)
```

---

## スレッドモデル

```
メインスレッド (TKinter event loop)
    │
    ├─ Generate 押下 → threading.Thread(target=run) 起動
    │                    │
    ├─ ProgressDialog 表示   generate_file() 実行
    │   ↑ after(100ms) ポーリング       │
    │                            cancel_event チェック
    └─ ダイアログ閉じ → cancel_event.set()
```

---

## 環境変数

| 変数名 | 説明 |
|---|---|
| `CORE_DIRECTION_MODEL_DIR` | コア指示モデル `.md` ファイルが格納されたディレクトリへのパス |

---

## テスト戦略

- **ユニットテスト**: `unittest.mock` で外部依存（ファイルシステム、環境変数、TKinter ダイアログ）をモック
- **カバレッジ目標**: 90% 以上（実績: 97%+）
- **TKinter 注意点**: Windows Store 版 Python では `tk.Tk()` の複数インスタンス生成が制限されるため、`conftest.py` でセッションスコープの共有 root を定義
