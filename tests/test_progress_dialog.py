"""
[ぐんまちゃん] ProgressDialog のユニットテストです。
スレッドの完了・エラー・キャンセルの各シナリオを検証します。
"""

import threading
from unittest.mock import MagicMock, patch

import pytest

from src.components.progress_dialog import ProgressDialog


@pytest.fixture
def mock_thread_done():
    """すでに終了した状態のスレッドモックです。"""
    thread = MagicMock(spec=threading.Thread)
    thread.is_alive.return_value = False
    return thread


@pytest.fixture
def mock_thread_running():
    """実行中のスレッドモックです。"""
    thread = MagicMock(spec=threading.Thread)
    thread.is_alive.return_value = True
    return thread


@pytest.fixture
def cancel_event():
    return threading.Event()


class TestProgressDialogCreation:
    """ProgressDialog の作成・表示テストです。"""

    def test_creates_without_error_on_success(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": True, "error": None, "path": "/some/output.md"}
        with patch("src.components.progress_dialog.messagebox.showinfo"):
            ProgressDialog(tk_root, cancel_event, mock_thread_done, result)
            try:
                tk_root.update()
            except Exception:
                pass

    def test_creation_with_error_result(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": False, "error": "Something went wrong", "path": None}
        with patch("src.components.progress_dialog.messagebox.showerror"):
            ProgressDialog(tk_root, cancel_event, mock_thread_done, result)
            try:
                tk_root.update()
            except Exception:
                pass

    def test_creation_with_cancelled_result(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": False, "error": "cancelled", "path": None}
        ProgressDialog(tk_root, cancel_event, mock_thread_done, result)
        try:
            tk_root.update()
        except Exception:
            pass


class TestProgressDialogPollProgress:
    """_poll_progress メソッドのテストです。"""

    def test_calls_on_generation_complete_when_thread_done(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": True, "error": None, "path": "/output.md"}
        dialog = ProgressDialog.__new__(ProgressDialog)
        dialog._cancel_event = cancel_event
        dialog._thread = mock_thread_done
        dialog._result = result
        dialog._generation_done = False

        with patch.object(dialog, "_on_generation_complete") as mock_complete:
            dialog._poll_progress()
            mock_complete.assert_called_once()

    def test_schedules_next_poll_when_thread_alive(
        self, tk_root, cancel_event, mock_thread_running
    ):
        result = {"success": False, "error": None, "path": None}
        dialog = ProgressDialog.__new__(ProgressDialog)
        dialog._cancel_event = cancel_event
        dialog._thread = mock_thread_running
        dialog._result = result
        dialog._generation_done = False

        with patch.object(dialog, "after") as mock_after:
            dialog._poll_progress()
            mock_after.assert_called_once_with(
                ProgressDialog.POLL_INTERVAL_MS, dialog._poll_progress
            )


class TestProgressDialogOnGenerationComplete:
    """_on_generation_complete メソッドのテストです。"""

    def _make_dialog(self, tk_root, cancel_event, thread, result):
        dialog = ProgressDialog.__new__(ProgressDialog)
        dialog._cancel_event = cancel_event
        dialog._thread = thread
        dialog._result = result
        dialog._generation_done = False
        dialog._progressbar = MagicMock()
        return dialog

    def test_shows_success_message_on_success(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": True, "error": None, "path": "/out/proj.md"}
        dialog = self._make_dialog(tk_root, cancel_event, mock_thread_done, result)
        with (
            patch("src.components.progress_dialog.messagebox.showinfo") as mock_info,
            patch.object(dialog, "destroy"),
        ):
            dialog._on_generation_complete()
            mock_info.assert_called_once()
            assert "/out/proj.md" in mock_info.call_args[0][1]

    def test_shows_error_message_on_failure(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": False, "error": "Write failed", "path": None}
        dialog = self._make_dialog(tk_root, cancel_event, mock_thread_done, result)
        with (
            patch("src.components.progress_dialog.messagebox.showerror") as mock_err,
            patch.object(dialog, "destroy"),
        ):
            dialog._on_generation_complete()
            mock_err.assert_called_once()
            assert "Write failed" in mock_err.call_args[0][1]

    def test_destroys_on_cancelled(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": False, "error": "cancelled", "path": None}
        dialog = self._make_dialog(tk_root, cancel_event, mock_thread_done, result)
        with patch.object(dialog, "destroy") as mock_destroy:
            dialog._on_generation_complete()
            mock_destroy.assert_called_once()

    def test_no_double_call_when_already_done(
        self, tk_root, cancel_event, mock_thread_done
    ):
        result = {"success": True, "error": None, "path": "/out.md"}
        dialog = self._make_dialog(tk_root, cancel_event, mock_thread_done, result)
        dialog._generation_done = True

        with patch("src.components.progress_dialog.messagebox.showinfo") as mock_info:
            dialog._on_generation_complete()
            mock_info.assert_not_called()


class TestProgressDialogOnClose:
    """_on_close メソッドのテストです。"""

    def _make_dialog(self, cancel_event, thread):
        dialog = ProgressDialog.__new__(ProgressDialog)
        dialog._cancel_event = cancel_event
        dialog._thread = thread
        dialog._generation_done = False
        return dialog

    def test_sets_cancel_event_when_thread_alive(
        self, cancel_event, mock_thread_running
    ):
        dialog = self._make_dialog(cancel_event, mock_thread_running)
        with patch.object(dialog, "destroy"):
            dialog._on_close()
        assert cancel_event.is_set()

    def test_no_cancel_event_when_thread_done(
        self, cancel_event, mock_thread_done
    ):
        dialog = self._make_dialog(cancel_event, mock_thread_done)
        with patch.object(dialog, "destroy"):
            dialog._on_close()
        assert not cancel_event.is_set()

    def test_always_destroys(self, cancel_event, mock_thread_done):
        dialog = self._make_dialog(cancel_event, mock_thread_done)
        with patch.object(dialog, "destroy") as mock_destroy:
            dialog._on_close()
            mock_destroy.assert_called_once()
