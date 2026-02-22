# Projspec Builder バックエンドロジック API 仕様

このドキュメントは `src/utils/` 以下の内部ロジック関数の仕様を定義します。
これらは UI に依存しない純粋な Python 関数であり、`unittest.mock` でモック可能です。

---

## `src/utils/helpers.py`

### `check_environment() -> str`

起動時に `CORE_DIRECTION_MODEL_DIR` 環境変数を検証します。

**返り値:**
- `str` — 有効なディレクトリパス

**例外:**

| 条件 | 例外 |
|---|---|
| 環境変数が未設定 | `EnvironmentError` |
| ディレクトリが存在しない | `EnvironmentError` |
| `.md` ファイルが 0 件 | `EnvironmentError` |

---

### `get_core_direction_files(directory: str) -> list[str]`

指定ディレクトリから `.md` ファイル名一覧を取得します。

**引数:**
- `directory: str` — 検索対象ディレクトリパス

**返り値:**
- `list[str]` — `.md` ファイル名のソート済みリスト（サブディレクトリは除外）

**例外:** なし（ファイルが 0 件の場合は空リストを返す）

---

### `check_output_exists(output_dir: str, project_name: str) -> bool`

出力ファイルが既に存在するか確認します。

**引数:**
- `output_dir: str` — 出力先ディレクトリパス
- `project_name: str` — プロジェクト名（`.md` 拡張子は含めない）

**返り値:**
- `True` — `{output_dir}/{project_name}.md` が存在する
- `False` — 存在しない

---

### `generate_file(core_dir, core_file, project_name, project_root_dir, output_dir, cancel_event=None) -> str`

コア指示ファイルをテンプレートとして出力 Markdown を生成します。

**引数:**

| 引数 | 型 | 説明 |
|---|---|---|
| `core_dir` | `str` | コア指示ファイルのディレクトリ |
| `core_file` | `str` | ファイル名（`.md` 含む） |
| `project_name` | `str` | `{{project_name}}` の置換値 |
| `project_root_dir` | `str` | `{{project_root_dir}}` の置換値 |
| `output_dir` | `str` | 出力先ディレクトリ |
| `cancel_event` | `threading.Event \| None` | キャンセル通知用イベント（省略可） |

**返り値:**
- `str` — 生成されたファイルの絶対パス

**例外:**

| 条件 | 例外 |
|---|---|
| `cancel_event` がセット済み | `InterruptedError` |
| `core_file` が存在しない | `FileNotFoundError` |
| ファイル I/O 失敗 | `OSError` |

**エンコーディング:**
- 読み込み: UTF-8（失敗時 CP932 にフォールバック）
- 書き出し: UTF-8

---

## `src/utils/validators.py`

### `ProjectFormData` (Pydantic BaseModel)

フォーム入力データの一括バリデーションモデルです。

**フィールド:**

| フィールド名 | 型 | バリデーション |
|---|---|---|
| `project_name` | `str` | 3〜50文字、正規表現 `^[a-zA-Z0-9_-]+$` |
| `project_root_dir` | `str` | 必須 |
| `core_direction_file` | `str` | 必須 |
| `output_dir` | `str` | 必須 |

**バリデーションエラー:**
- `pydantic.ValidationError` — いずれかの制約違反時に送出

---

## プレースホルダー仕様

コア指示ファイル内で使用できるプレースホルダー:

| プレースホルダー | 置換される値 |
|---|---|
| `{{project_name}}` | フォームの Project Name 入力値 |
| `{{project_root_dir}}` | フォームの Project Root Directory 入力値 |
