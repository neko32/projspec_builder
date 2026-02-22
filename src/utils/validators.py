"""
[さのまる] フォームデータのバリデーションモデルまる。
Pydantic の Annotated を使って入力値を検証するまる。
"""

import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class ProjectFormData(BaseModel):
    """プロジェクト生成フォームの入力データモデルまる。"""

    project_name: Annotated[str, Field(min_length=3, max_length=50)]
    project_root_dir: str
    core_direction_file: str
    output_dir: str

    @field_validator("project_name")
    @classmethod
    def validate_project_name_chars(cls, v: str) -> str:
        """英数字・ハイフン・アンダースコアのみ許可するまる。"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Project name には英数字・ハイフン・アンダースコアのみ使用できます。"
            )
        return v
