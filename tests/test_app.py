"""
[ぐんまちゃん] アプリケーションクラスのユニットテストです。
TKinter の外部依存は unittest.mock でモックしています。
"""

from unittest.mock import MagicMock, patch

import pytest

from src.app import ProjspecBuilderApp


@pytest.fixture
def mock_env(tmp_path, monkeypatch):
    """有効な CORE_DIRECTION_MODEL_DIR 環境変数をモックします。"""
    (tmp_path / "SMARU v.1.2.md").write_text("# {{project_name}}\nRoot: {{project_root_dir}}")
    (tmp_path / "Other Model.md").write_text("# Other")
    monkeypatch.setenv("CORE_DIRECTION_MODEL_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def app(tk_root, mock_env):
    """初期化済みのアプリインスタンスを提供します。"""
    application = ProjspecBuilderApp(tk_root)
    return application


class TestAppInitialization:
    """アプリ初期化のテストです。"""

    def test_initializes_successfully_with_valid_env(self, app):
        assert app._initialized is True

    def test_core_dir_is_set(self, app, mock_env):
        assert app._core_dir == str(mock_env)

    def test_core_files_loaded(self, app):
        assert len(app._core_files) == 2
        assert "SMARU v.1.2.md" in app._core_files
        assert "Other Model.md" in app._core_files

    def test_generate_button_disabled_initially(self, app):
        assert str(app._generate_btn["state"]) == "disabled"

    def test_default_core_file_set(self, app):
        assert app._core_file_var.get() == "SMARU v.1.2"

    def test_env_error_shows_messagebox_and_destroys(self, tk_root, monkeypatch):
        monkeypatch.delenv("CORE_DIRECTION_MODEL_DIR", raising=False)
        with (
            patch("src.app.messagebox.showerror") as mock_err,
            patch.object(tk_root, "after"),  # セッション共有 root の破壊を防ぐ
        ):
            application = ProjspecBuilderApp(tk_root)
            assert application._initialized is False
            mock_err.assert_called_once()

    def test_first_file_as_default_when_smaru_not_present(
        self, tk_root, tmp_path, monkeypatch
    ):
        (tmp_path / "alpha.md").write_text("content")
        monkeypatch.setenv("CORE_DIRECTION_MODEL_DIR", str(tmp_path))
        application = ProjspecBuilderApp(tk_root)
        assert application._core_file_var.get() == "alpha"


class TestGenerateButtonState:
    """Generate ボタンの有効/無効状態のテストです。"""

    def test_button_enabled_when_all_fields_filled(self, app, mock_env, tmp_path):
        app._project_name_var.set("my-project")
        app._project_root_var.set(str(tmp_path))
        app._core_file_var.set("SMARU v.1.2")
        app._output_dir_var.set(str(tmp_path))
        assert str(app._generate_btn["state"]) == "normal"

    def test_button_disabled_when_name_empty(self, app, tmp_path):
        app._project_name_var.set("")
        app._project_root_var.set(str(tmp_path))
        app._core_file_var.set("SMARU v.1.2")
        app._output_dir_var.set(str(tmp_path))
        assert str(app._generate_btn["state"]) == "disabled"

    def test_button_disabled_when_root_dir_empty(self, app, tmp_path):
        app._project_name_var.set("my-project")
        app._project_root_var.set("")
        app._core_file_var.set("SMARU v.1.2")
        app._output_dir_var.set(str(tmp_path))
        assert str(app._generate_btn["state"]) == "disabled"

    def test_button_disabled_when_output_dir_empty(self, app, tmp_path):
        app._project_name_var.set("my-project")
        app._project_root_var.set(str(tmp_path))
        app._core_file_var.set("SMARU v.1.2")
        app._output_dir_var.set("")
        assert str(app._generate_btn["state"]) == "disabled"


class TestOnGenerate:
    """Generate ボタン押下処理のテストです。"""

    def _fill_form(self, app, output_dir):
        app._project_name_var.set("my-project")
        app._project_root_var.set("/some/root")
        app._core_file_var.set("SMARU v.1.2")
        app._output_dir_var.set(str(output_dir))

    def test_generate_shows_error_when_output_exists(self, app, mock_env, tmp_path):
        (tmp_path / "my-project.md").write_text("existing")
        self._fill_form(app, tmp_path)
        with patch("src.app.messagebox.showerror") as mock_err:
            app._on_generate()
            mock_err.assert_called_once()
            assert "既に存在" in mock_err.call_args[0][1]

    def test_generate_shows_error_for_invalid_project_name(
        self, app, mock_env, tmp_path
    ):
        app._project_name_var.set("invalid name!")
        app._project_root_var.set("/some/root")
        app._core_file_var.set("SMARU v.1.2")
        app._output_dir_var.set(str(tmp_path))
        with patch("src.app.messagebox.showerror") as mock_err:
            app._on_generate()
            mock_err.assert_called_once()

    def test_generate_starts_thread_and_shows_dialog(self, app, mock_env, tmp_path):
        self._fill_form(app, tmp_path)
        with patch("src.app.ProgressDialog") as mock_dialog_cls:
            mock_dialog = MagicMock()
            mock_dialog_cls.return_value = mock_dialog
            app._on_generate()
            mock_dialog_cls.assert_called_once()
            mock_dialog.wait_window.assert_called_once()


class TestOnClear:
    """Clear ボタン押下処理のテストです。"""

    def test_clear_resets_fields_when_confirmed(self, app, mock_env):
        app._project_name_var.set("my-project")
        app._project_root_var.set("/some/root")
        app._output_dir_var.set("/some/output")

        with patch("src.app.messagebox.askyesno", return_value=True):
            app._on_clear()

        assert app._project_name_var.get() == ""
        assert app._project_root_var.get() == ""
        assert app._output_dir_var.get() == ""
        assert app._core_file_var.get() == "SMARU v.1.2"

    def test_clear_does_nothing_when_cancelled(self, app):
        app._project_name_var.set("my-project")

        with patch("src.app.messagebox.askyesno", return_value=False):
            app._on_clear()

        assert app._project_name_var.get() == "my-project"

    def test_clear_sets_focus_to_project_name(self, app):
        with patch("src.app.messagebox.askyesno", return_value=True):
            with patch.object(app._project_name_entry, "focus") as mock_focus:
                app._on_clear()
                mock_focus.assert_called_once()


class TestBrowseButtons:
    """ブラウズボタンのテストです。"""

    def test_browse_root_dir_sets_variable(self, app):
        with patch("src.app.filedialog.askdirectory", return_value="/selected/path"):
            app._browse_root_dir()
        assert app._project_root_var.get() == "/selected/path"

    def test_browse_root_dir_does_nothing_when_cancelled(self, app):
        app._project_root_var.set("/original")
        with patch("src.app.filedialog.askdirectory", return_value=""):
            app._browse_root_dir()
        assert app._project_root_var.get() == "/original"

    def test_browse_output_dir_sets_variable(self, app):
        with patch("src.app.filedialog.askdirectory", return_value="/output/path"):
            app._browse_output_dir()
        assert app._output_dir_var.get() == "/output/path"

    def test_browse_output_dir_does_nothing_when_cancelled(self, app):
        app._output_dir_var.set("/original")
        with patch("src.app.filedialog.askdirectory", return_value=""):
            app._browse_output_dir()
        assert app._output_dir_var.get() == "/original"


class TestStartGeneration:
    """_start_generation メソッドのテストです。"""

    def test_result_populated_on_success(self, app, mock_env, tmp_path):
        result = {}

        def fake_dialog(parent, cancel_event, thread, res):
            thread.join(timeout=5)
            result.update(res)
            mock = MagicMock()
            mock.wait_window = MagicMock()
            return mock

        with patch("src.app.ProgressDialog", side_effect=fake_dialog):
            app._start_generation(
                "test-proj", "/root", "SMARU v.1.2.md", str(tmp_path)
            )

        assert result.get("success") is True
        assert result.get("path") is not None
