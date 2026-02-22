"""
[ぐんまちゃん] pytest 共通フィクスチャの定義です。
Windows Store 版 Python では Tk() の複数インスタンス生成ができないため、
セッション単位で共有する TK ルートウィンドウを定義しています。
"""

import tkinter as tk

import pytest


@pytest.fixture(scope="session")
def tk_root():
    """テストセッション全体で共有する TKinter ルートウィンドウです。"""
    root = tk.Tk()
    root.withdraw()
    yield root
    try:
        root.destroy()
    except Exception:
        pass
