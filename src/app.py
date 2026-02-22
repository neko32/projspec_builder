"""
[ふっかちゃん] メインアプリケーションクラスだよ～。
TKinter でシングルページのプロジェクト仕様生成フォームを提供するよ～。
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.components.progress_dialog import ProgressDialog
from src.utils.helpers import (
    check_environment,
    check_output_exists,
    generate_file,
    get_core_direction_files,
)
from src.utils.validators import ProjectFormData

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 620
PADDING_X = 100
BASE_COLOR = "#7297c5"
SECONDARY_COLOR = "#666666"
ICON_PATH = r"C:\resources\projspec_builder\app_icon.png"
DEFAULT_CORE_FILE = "SMARU v.1.2"


class ProjspecBuilderApp:
    """プロジェクト仕様書生成アプリのメインクラスだよ～。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._core_dir: str = ""
        self._core_files: list[str] = []
        self._initialized = False

        if not self._run_startup_checks():
            return

        self._setup_window()
        self._setup_styles()
        self._create_widgets()
        self._setup_traces()
        self._update_generate_button_state()
        self._initialized = True

    # ------------------------------------------------------------------ #
    # 起動チェック
    # ------------------------------------------------------------------ #

    def _run_startup_checks(self) -> bool:
        """環境変数チェックを実行して問題があればエラーを表示するまる。"""
        try:
            self._core_dir = check_environment()
            self._core_files = get_core_direction_files(self._core_dir)
            return True
        except EnvironmentError as exc:
            messagebox.showerror("起動エラー", str(exc))
            self.root.after(100, self.root.destroy)
            return False

    # ------------------------------------------------------------------ #
    # ウィンドウ・スタイル設定
    # ------------------------------------------------------------------ #

    def _setup_window(self) -> None:
        self.root.title("Projspec Builder")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="white")

        try:
            icon = tk.PhotoImage(file=ICON_PATH)
            self.root.iconphoto(True, icon)
        except Exception:
            pass  # アイコンが無くてもアプリは動作するよ～

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabel", foreground=SECONDARY_COLOR, font=("Segoe UI", 10))
        style.configure(
            "Header.TLabel",
            foreground=BASE_COLOR,
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "Generate.TButton",
            foreground="white",
            background=BASE_COLOR,
            font=("Segoe UI", 10, "bold"),
            padding=(20, 6),
        )
        style.map(
            "Generate.TButton",
            background=[("disabled", "#b0c4de"), ("active", "#5a7fb5")],
            foreground=[("disabled", "#888888")],
        )
        style.configure(
            "Clear.TButton",
            foreground=SECONDARY_COLOR,
            background="#e8e8e8",
            font=("Segoe UI", 10),
            padding=(20, 6),
        )
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=6)

    # ------------------------------------------------------------------ #
    # ウィジェット作成
    # ------------------------------------------------------------------ #

    def _create_widgets(self) -> None:
        # スクロール可能なメインフレーム
        main_frame = ttk.Frame(self.root, padding=(PADDING_X, 30, PADDING_X, 30))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        ttk.Label(main_frame, text="Projspec Builder", style="Header.TLabel").pack(
            anchor=tk.W, pady=(0, 24)
        )

        # Project Name
        self._project_name_var = tk.StringVar()
        ttk.Label(main_frame, text="Project Name").pack(anchor=tk.W)
        self._project_name_entry = ttk.Entry(
            main_frame, textvariable=self._project_name_var
        )
        self._project_name_entry.pack(fill=tk.X, pady=(4, 16))

        # Project Root Directory
        self._project_root_var = tk.StringVar()
        ttk.Label(main_frame, text="Project Root Directory").pack(anchor=tk.W)
        root_row = ttk.Frame(main_frame)
        root_row.pack(fill=tk.X, pady=(4, 16))
        ttk.Entry(root_row, textvariable=self._project_root_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(root_row, text="Browse…", command=self._browse_root_dir).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        # Core Direction File
        self._core_file_var = tk.StringVar()
        ttk.Label(main_frame, text="Core Direction File").pack(anchor=tk.W)
        display_names = [f[:-3] for f in self._core_files]  # .md を除いた表示名
        self._core_file_combo = ttk.Combobox(
            main_frame,
            textvariable=self._core_file_var,
            values=display_names,
            state="readonly",
        )
        self._core_file_combo.pack(fill=tk.X, pady=(4, 16))
        self._set_default_core_file(display_names)

        # Output Directory
        self._output_dir_var = tk.StringVar()
        ttk.Label(main_frame, text="Output Directory").pack(anchor=tk.W)
        output_row = ttk.Frame(main_frame)
        output_row.pack(fill=tk.X, pady=(4, 16))
        ttk.Entry(output_row, textvariable=self._output_dir_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(output_row, text="Browse…", command=self._browse_output_dir).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        # ボタン行
        button_row = ttk.Frame(main_frame)
        button_row.pack(anchor=tk.W, pady=(8, 0))
        self._generate_btn = ttk.Button(
            button_row,
            text="Generate",
            style="Generate.TButton",
            command=self._on_generate,
            state=tk.DISABLED,
        )
        self._generate_btn.pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(
            button_row,
            text="Clear",
            style="Clear.TButton",
            command=self._on_clear,
        ).pack(side=tk.LEFT)

    def _set_default_core_file(self, display_names: list[str]) -> None:
        """デフォルト値を設定するよ～。"""
        if DEFAULT_CORE_FILE in display_names:
            self._core_file_var.set(DEFAULT_CORE_FILE)
        elif display_names:
            self._core_file_var.set(display_names[0])

    # ------------------------------------------------------------------ #
    # フォーム状態管理
    # ------------------------------------------------------------------ #

    def _setup_traces(self) -> None:
        for var in (
            self._project_name_var,
            self._project_root_var,
            self._core_file_var,
            self._output_dir_var,
        ):
            var.trace_add("write", self._on_form_change)

    def _on_form_change(self, *_args: object) -> None:
        self._update_generate_button_state()

    def _update_generate_button_state(self) -> None:
        all_filled = all(
            [
                self._project_name_var.get().strip(),
                self._project_root_var.get().strip(),
                self._core_file_var.get().strip(),
                self._output_dir_var.get().strip(),
            ]
        )
        self._generate_btn.config(state=tk.NORMAL if all_filled else tk.DISABLED)

    # ------------------------------------------------------------------ #
    # ブラウズボタン
    # ------------------------------------------------------------------ #

    def _browse_root_dir(self) -> None:
        directory = filedialog.askdirectory(
            title="Project Root Directory を選択してください"
        )
        if directory:
            self._project_root_var.set(directory)

    def _browse_output_dir(self) -> None:
        directory = filedialog.askdirectory(title="Output Directory を選択してください")
        if directory:
            self._output_dir_var.set(directory)

    # ------------------------------------------------------------------ #
    # Generate
    # ------------------------------------------------------------------ #

    def _on_generate(self) -> None:
        project_name = self._project_name_var.get().strip()
        project_root = self._project_root_var.get().strip()
        core_display = self._core_file_var.get().strip()
        output_dir = self._output_dir_var.get().strip()

        # Pydantic バリデーション
        try:
            ProjectFormData(
                project_name=project_name,
                project_root_dir=project_root,
                core_direction_file=core_display + ".md",
                output_dir=output_dir,
            )
        except Exception as exc:
            messagebox.showerror("入力エラー", str(exc))
            return

        # 出力ファイル重複チェック
        if check_output_exists(output_dir, project_name):
            messagebox.showerror(
                "エラー",
                f"出力ファイルが既に存在します。\n\n"
                f"{output_dir}\\{project_name}.md\n\n"
                "別の Output Directory または Project Name を指定してください。",
            )
            return

        core_file = core_display + ".md"
        self._start_generation(project_name, project_root, core_file, output_dir)

    def _start_generation(
        self,
        project_name: str,
        project_root: str,
        core_file: str,
        output_dir: str,
    ) -> None:
        """バックグラウンドスレッドでファイル生成を開始するよ～。"""
        cancel_event = threading.Event()
        result: dict = {"success": False, "error": None, "path": None}

        def run() -> None:
            try:
                path = generate_file(
                    self._core_dir,
                    core_file,
                    project_name,
                    project_root,
                    output_dir,
                    cancel_event,
                )
                result["success"] = True
                result["path"] = path
            except InterruptedError:
                result["error"] = "cancelled"
            except Exception as exc:
                result["error"] = str(exc)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        dialog = ProgressDialog(self.root, cancel_event, thread, result)
        dialog.wait_window()

    # ------------------------------------------------------------------ #
    # Clear
    # ------------------------------------------------------------------ #

    def _on_clear(self) -> None:
        if not messagebox.askyesno("確認", "入力を本当にクリアしますか？"):
            return

        self._project_name_var.set("")
        self._project_root_var.set("")
        display_names = [f[:-3] for f in self._core_files]
        self._set_default_core_file(display_names)
        self._output_dir_var.set("")
        self._project_name_entry.focus()
