"""
[さのまる] アプリのエントリーポイントまる。
Tk ルートウィンドウを生成して ProjspecBuilderApp を起動するまる。
"""

import tkinter as tk

from src.app import ProjspecBuilderApp


def main() -> None:  # pragma: no cover
    root = tk.Tk()
    ProjspecBuilderApp(root)
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()
