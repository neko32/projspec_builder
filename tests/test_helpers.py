"""
[ぐんまちゃん] ヘルパー関数のユニットテストです。
環境チェック・ファイル一覧取得・ファイル生成ロジックを検証します。
外部依存は unittest.mock でモックしています。
"""

import os
import threading

import pytest

from src.utils.helpers import (
    check_environment,
    check_output_exists,
    generate_file,
    get_core_direction_files,
)


class TestCheckEnvironment:
    """check_environment 関数のテストです。"""

    def test_missing_env_var_raises(self, monkeypatch):
        monkeypatch.delenv("CORE_DIRECTION_MODEL_DIR", raising=False)
        with pytest.raises(EnvironmentError, match="CORE_DIRECTION_MODEL_DIR"):
            check_environment()

    def test_nonexistent_directory_raises(self, monkeypatch):
        monkeypatch.setenv("CORE_DIRECTION_MODEL_DIR", "/nonexistent/path/xyz")
        with pytest.raises(EnvironmentError, match="ディレクトリが存在しません"):
            check_environment()

    def test_empty_directory_raises(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORE_DIRECTION_MODEL_DIR", str(tmp_path))
        with pytest.raises(EnvironmentError, match=".md"):
            check_environment()

    def test_directory_with_only_non_md_files_raises(self, tmp_path, monkeypatch):
        (tmp_path / "readme.txt").write_text("content")
        monkeypatch.setenv("CORE_DIRECTION_MODEL_DIR", str(tmp_path))
        with pytest.raises(EnvironmentError, match=".md"):
            check_environment()

    def test_valid_directory_returns_path(self, tmp_path, monkeypatch):
        (tmp_path / "template.md").write_text("# Template")
        monkeypatch.setenv("CORE_DIRECTION_MODEL_DIR", str(tmp_path))
        result = check_environment()
        assert result == str(tmp_path)

    def test_valid_directory_with_multiple_md_files(self, tmp_path, monkeypatch):
        (tmp_path / "file1.md").write_text("content1")
        (tmp_path / "file2.md").write_text("content2")
        monkeypatch.setenv("CORE_DIRECTION_MODEL_DIR", str(tmp_path))
        result = check_environment()
        assert result == str(tmp_path)


class TestGetCoreDirectionFiles:
    """get_core_direction_files 関数のテストです。"""

    def test_returns_md_files_only(self, tmp_path):
        (tmp_path / "template.md").write_text("content")
        (tmp_path / "other.txt").write_text("content")
        (tmp_path / "readme.rst").write_text("content")

        files = get_core_direction_files(str(tmp_path))
        assert files == ["template.md"]

    def test_excludes_directories(self, tmp_path):
        (tmp_path / "subdir.md").mkdir()
        (tmp_path / "file.md").write_text("content")

        files = get_core_direction_files(str(tmp_path))
        assert "subdir.md" not in files
        assert "file.md" in files

    def test_returns_sorted_list(self, tmp_path):
        (tmp_path / "c_file.md").write_text("content")
        (tmp_path / "a_file.md").write_text("content")
        (tmp_path / "b_file.md").write_text("content")

        files = get_core_direction_files(str(tmp_path))
        assert files == ["a_file.md", "b_file.md", "c_file.md"]

    def test_empty_directory_returns_empty_list(self, tmp_path):
        files = get_core_direction_files(str(tmp_path))
        assert files == []

    def test_multiple_md_files(self, tmp_path):
        for name in ["alpha.md", "beta.md", "gamma.md"]:
            (tmp_path / name).write_text("content")

        files = get_core_direction_files(str(tmp_path))
        assert len(files) == 3
        assert "alpha.md" in files


class TestCheckOutputExists:
    """check_output_exists 関数のテストです。"""

    def test_file_exists_returns_true(self, tmp_path):
        (tmp_path / "myproject.md").write_text("content")
        assert check_output_exists(str(tmp_path), "myproject") is True

    def test_file_not_exists_returns_false(self, tmp_path):
        assert check_output_exists(str(tmp_path), "myproject") is False

    def test_different_name_not_found(self, tmp_path):
        (tmp_path / "other.md").write_text("content")
        assert check_output_exists(str(tmp_path), "myproject") is False

    def test_constructs_correct_path(self, tmp_path):
        project_name = "test-project"
        (tmp_path / f"{project_name}.md").write_text("content")
        assert check_output_exists(str(tmp_path), project_name) is True


class TestGenerateFile:
    """generate_file 関数のテストです。"""

    def test_basic_generation(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "template.md").write_text(
            "# {{project_name}}\nRoot: {{project_root_dir}}"
        )
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = generate_file(
            str(core_dir), "template.md", "my-project", "/my/root", str(output_dir)
        )

        assert os.path.exists(result)
        content = open(result, encoding="utf-8").read()
        assert "my-project" in content
        assert "/my/root" in content
        assert "{{project_name}}" not in content
        assert "{{project_root_dir}}" not in content

    def test_output_filename_is_project_name_md(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "template.md").write_text("content")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = generate_file(
            str(core_dir), "template.md", "my-project", "/root", str(output_dir)
        )
        assert os.path.basename(result) == "my-project.md"

    def test_placeholder_replacement(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        template_content = (
            "Project: {{project_name}}\n"
            "Root: {{project_root_dir}}\n"
            "Again: {{project_name}}"
        )
        (core_dir / "template.md").write_text(template_content)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = generate_file(
            str(core_dir), "template.md", "hello", "/world", str(output_dir)
        )

        content = open(result, encoding="utf-8").read()
        assert content == "Project: hello\nRoot: /world\nAgain: hello"

    def test_cancellation_before_write(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "template.md").write_text("content")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        cancel_event = threading.Event()
        cancel_event.set()

        with pytest.raises(InterruptedError):
            generate_file(
                str(core_dir),
                "template.md",
                "my-project",
                "/root",
                str(output_dir),
                cancel_event,
            )

        assert not (output_dir / "my-project.md").exists()

    def test_no_cancellation_when_event_not_set(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "template.md").write_text("content")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        cancel_event = threading.Event()

        result = generate_file(
            str(core_dir),
            "template.md",
            "my-project",
            "/root",
            str(output_dir),
            cancel_event,
        )
        assert os.path.exists(result)

    def test_missing_template_raises(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises((FileNotFoundError, OSError)):
            generate_file(
                str(core_dir),
                "nonexistent.md",
                "my-project",
                "/root",
                str(output_dir),
            )

    def test_generates_utf8_output(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "template.md").write_text("日本語テスト: {{project_name}}", encoding="utf-8")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = generate_file(
            str(core_dir), "template.md", "test", "/root", str(output_dir)
        )

        content = open(result, encoding="utf-8").read()
        assert "日本語テスト: test" in content

    def test_without_cancel_event(self, tmp_path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "template.md").write_text("{{project_name}}")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = generate_file(
            str(core_dir), "template.md", "proj", "/dir", str(output_dir)
        )
        assert os.path.exists(result)
