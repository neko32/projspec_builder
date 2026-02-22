"""
[さのまる] 環境チェック・ファイル一覧取得・ファイル生成ロジックまる。
外部依存は unittest.mock でモック可能な設計にしてあるまる。
"""

import os
import threading
from pathlib import Path


def check_environment() -> str:
    """CORE_DIRECTION_MODEL_DIR 環境変数を検証して返すまる。

    Returns:
        有効なディレクトリパス文字列。

    Raises:
        EnvironmentError: 環境変数が未設定・ディレクトリが無効・mdファイル不在の場合。
    """
    env_dir = os.environ.get("CORE_DIRECTION_MODEL_DIR")
    if not env_dir:
        raise EnvironmentError(
            "環境変数 CORE_DIRECTION_MODEL_DIR が設定されていません。\n"
            "CORE_DIRECTION_MODEL_DIR を設定してからアプリを再起動してください。"
        )
    if not os.path.isdir(env_dir):
        raise EnvironmentError(
            f"ディレクトリが存在しません: {env_dir}\n"
            "CORE_DIRECTION_MODEL_DIR に正しいパスを設定してください。"
        )
    md_files = get_core_direction_files(env_dir)
    if not md_files:
        raise EnvironmentError(
            f".md ファイルが見つかりません: {env_dir}\n"
            "コア指示モデルの .md ファイルをディレクトリに配置してください。"
        )
    return env_dir


def get_core_direction_files(directory: str) -> list[str]:
    """指定ディレクトリから .md ファイル名一覧をソート順で返すまる。

    Args:
        directory: 検索対象のディレクトリパス。

    Returns:
        .md ファイル名のソート済みリスト。
    """
    return sorted(
        f
        for f in os.listdir(directory)
        if f.endswith(".md") and os.path.isfile(os.path.join(directory, f))
    )


def check_output_exists(output_dir: str, project_name: str) -> bool:
    """出力ファイルが既に存在するか確認するまる。

    Args:
        output_dir: 出力先ディレクトリパス。
        project_name: プロジェクト名 (.md 拡張子は含めない)。

    Returns:
        ファイルが存在する場合 True。
    """
    output_path = Path(output_dir) / f"{project_name}.md"
    return output_path.exists()


def generate_file(
    core_dir: str,
    core_file: str,
    project_name: str,
    project_root_dir: str,
    output_dir: str,
    cancel_event: threading.Event | None = None,
) -> str:
    """コア指示ファイルをテンプレートとして出力 .md を生成するまる。

    プレースホルダー置換後にキャンセル確認してから書き出すまる。

    Args:
        core_dir: コア指示ファイルが格納されているディレクトリ。
        core_file: 読み込むファイル名 (.md 含む)。
        project_name: {{project_name}} の置換値。
        project_root_dir: {{project_root_dir}} の置換値。
        output_dir: 出力先ディレクトリ。
        cancel_event: キャンセル通知用イベント (省略可)。

    Returns:
        生成されたファイルの絶対パス文字列。

    Raises:
        InterruptedError: cancel_event がセットされている場合。
        FileNotFoundError: コア指示ファイルが存在しない場合。
        OSError: ファイル読み書きに失敗した場合。
    """
    core_file_path = Path(core_dir) / core_file

    # コア指示ファイルの読み込み (UTF-8 → CP932 フォールバック)
    try:
        content = core_file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = core_file_path.read_text(encoding="cp932")

    # プレースホルダー置換
    content = content.replace("{{project_name}}", project_name)
    content = content.replace("{{project_root_dir}}", project_root_dir)

    # キャンセル確認 (書き込み前)
    if cancel_event is not None and cancel_event.is_set():
        raise InterruptedError("ファイル生成がキャンセルされました。")

    # 出力ファイルへの書き込み
    output_path = Path(output_dir) / f"{project_name}.md"
    output_path.write_text(content, encoding="utf-8")

    return str(output_path)
