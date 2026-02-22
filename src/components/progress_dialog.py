"""
[ふっかちゃん] ファイル生成中に表示するモーダル進捗ダイアログだよ～。
スレッド完了をポーリングして結果を通知するよ～。
"""

import threading
import tkinter as tk
from tkinter import messagebox, ttk


class ProgressDialog(tk.Toplevel):
    """ファイル生成中に表示するモーダルダイアログだよ～。

    生成スレッドが完了するまでポーリングし、
    ユーザーが閉じたらキャンセルイベントをセットするよ～。
    """

    POLL_INTERVAL_MS = 100

    def __init__(
        self,
        parent: tk.Tk,
        cancel_event: threading.Event,
        thread: threading.Thread,
        result: dict,
    ) -> None:
        super().__init__(parent)
        self._cancel_event = cancel_event
        self._thread = thread
        self._result = result
        self._generation_done = False

        self._setup_window(parent)
        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._progressbar.start(10)
        self.after(self.POLL_INTERVAL_MS, self._poll_progress)

    def _setup_window(self, parent: tk.Tk) -> None:
        self.title("生成中...")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.geometry("360x120")

        # 親ウィンドウの中央に配置
        parent.update_idletasks()
        px = parent.winfo_x() + parent.winfo_width() // 2 - 180
        py = parent.winfo_y() + parent.winfo_height() // 2 - 60
        self.geometry(f"+{px}+{py}")

    def _create_widgets(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="ファイルを生成中です...しばらくお待ちください。").pack(
            anchor=tk.W, pady=(0, 10)
        )
        self._progressbar = ttk.Progressbar(frame, mode="indeterminate")
        self._progressbar.pack(fill=tk.X)

    def _poll_progress(self) -> None:
        """スレッドの完了を定期的に確認するよ～。"""
        if not self._thread.is_alive():
            self._on_generation_complete()
        else:
            self.after(self.POLL_INTERVAL_MS, self._poll_progress)

    def _on_generation_complete(self) -> None:
        """生成完了時の処理だよ～。"""
        if self._generation_done:
            return
        self._generation_done = True
        self._progressbar.stop()

        error = self._result.get("error")
        if error == "cancelled":
            self.destroy()
        elif error:
            messagebox.showerror(
                "生成失敗",
                f"ファイルの生成に失敗しました。\n\n{error}",
                parent=self,
            )
            self.destroy()
        else:
            output_path = self._result.get("path", "")
            messagebox.showinfo(
                "生成完了",
                f"ファイルが正常に生成されました。\n\n{output_path}",
                parent=self,
            )
            self.destroy()

    def _on_close(self) -> None:
        """ダイアログを閉じたとき、生成中ならキャンセルするよ～。"""
        if self._thread.is_alive():
            self._cancel_event.set()
        self.destroy()
