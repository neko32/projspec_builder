"""
[ぐんまちゃん] バリデーションロジックのユニットテストです。
ProjectFormData モデルの各フィールドのバリデーションを検証します。
"""

import pytest
from pydantic import ValidationError

from src.utils.validators import ProjectFormData


class TestProjectNameValidation:
    """Project Name フィールドのバリデーションテストです。"""

    def _make_data(self, project_name: str) -> dict:
        return {
            "project_name": project_name,
            "project_root_dir": "/some/path",
            "core_direction_file": "SMARU v.1.2.md",
            "output_dir": "/output/path",
        }

    def test_valid_alphanumeric(self):
        data = ProjectFormData(**self._make_data("myproject123"))
        assert data.project_name == "myproject123"

    def test_valid_with_hyphen(self):
        data = ProjectFormData(**self._make_data("my-project"))
        assert data.project_name == "my-project"

    def test_valid_with_underscore(self):
        data = ProjectFormData(**self._make_data("my_project"))
        assert data.project_name == "my_project"

    def test_valid_min_length(self):
        data = ProjectFormData(**self._make_data("abc"))
        assert data.project_name == "abc"

    def test_valid_max_length(self):
        name = "a" * 50
        data = ProjectFormData(**self._make_data(name))
        assert data.project_name == name

    def test_too_short_raises(self):
        with pytest.raises(ValidationError):
            ProjectFormData(**self._make_data("ab"))

    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            ProjectFormData(**self._make_data("a" * 51))

    def test_space_not_allowed(self):
        with pytest.raises(ValidationError):
            ProjectFormData(**self._make_data("my project"))

    def test_dot_not_allowed(self):
        with pytest.raises(ValidationError):
            ProjectFormData(**self._make_data("my.project"))

    def test_slash_not_allowed(self):
        with pytest.raises(ValidationError):
            ProjectFormData(**self._make_data("my/project"))

    def test_japanese_not_allowed(self):
        with pytest.raises(ValidationError):
            ProjectFormData(**self._make_data("テスト"))

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError):
            ProjectFormData(**self._make_data(""))

    def test_mixed_valid_chars(self):
        data = ProjectFormData(**self._make_data("My-Project_123"))
        assert data.project_name == "My-Project_123"


class TestProjectFormDataFields:
    """ProjectFormData 全フィールドのテストです。"""

    def test_all_fields_valid(self):
        data = ProjectFormData(
            project_name="test-project",
            project_root_dir="C:/dev/myapp",
            core_direction_file="SMARU v.1.2.md",
            output_dir="C:/output",
        )
        assert data.project_name == "test-project"
        assert data.project_root_dir == "C:/dev/myapp"
        assert data.core_direction_file == "SMARU v.1.2.md"
        assert data.output_dir == "C:/output"

    def test_missing_project_name_raises(self):
        with pytest.raises(ValidationError):
            ProjectFormData(
                project_root_dir="/some/path",
                core_direction_file="SMARU v.1.2.md",
                output_dir="/output",
            )

    def test_missing_project_root_dir_raises(self):
        with pytest.raises(ValidationError):
            ProjectFormData(
                project_name="test",
                core_direction_file="SMARU v.1.2.md",
                output_dir="/output",
            )

    def test_missing_core_direction_file_raises(self):
        with pytest.raises(ValidationError):
            ProjectFormData(
                project_name="test",
                project_root_dir="/some/path",
                output_dir="/output",
            )

    def test_missing_output_dir_raises(self):
        with pytest.raises(ValidationError):
            ProjectFormData(
                project_name="test",
                project_root_dir="/some/path",
                core_direction_file="SMARU v.1.2.md",
            )
