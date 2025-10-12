"""データモデルモジュール"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Literal, Optional

from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:
    pass


class FortuneRequest(BaseModel):
    """姓名判断リクエストモデル"""

    last_name: str = Field(..., min_length=1, max_length=10, description="姓")
    first_name: str = Field(..., min_length=1, max_length=10, description="名")
    gender: Literal["m", "f"] = Field(..., description="性別")

    @validator("last_name", "first_name")
    def validate_japanese_characters(cls, v: str) -> str:
        """日本語文字の検証"""
        if not v.strip():
            raise ValueError("空文字は許可されていません")
        return v.strip()


class StrokeAnalysisRequest(BaseModel):
    """画数分析リクエストモデル"""

    last_name: str = Field(..., min_length=1, max_length=10, description="姓")
    char_count: int = Field(..., ge=1, le=3, description="文字数")


class FortuneResult(BaseModel):
    """運勢結果モデル"""

    天格: Optional[str] = None
    人格: Optional[str] = None
    地格: Optional[str] = None
    外格: Optional[str] = None
    総格: Optional[str] = None
    三才配置: Optional[str] = None
    陰陽配列: Optional[str] = None
    仕事運: Optional[str] = None
    家庭運: Optional[str] = None


class FortuneResponse(BaseModel):
    """姓名判断レスポンスモデル"""

    enamae: FortuneResult
    namaeuranai: FortuneResult


class StrokePattern(BaseModel):
    """画数パターンモデル"""

    strokes: List[int] = Field(..., description="画数のリスト")
    characters: str = Field(..., description="対応する文字")
    enamae_result: FortuneResult
    namaeuranai_result: FortuneResult
    total_score: float = Field(..., ge=0, le=100, description="総合スコア")


class AnalysisResult(BaseModel):
    """分析結果モデル"""

    generated_at: datetime = Field(default_factory=datetime.now)
    last_name: str
    char_count: int = Field(..., ge=1, le=3)
    total_patterns: int = Field(..., ge=0)
    top_results: List[StrokePattern] = Field(..., max_length=20)


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル"""

    error: str = Field(..., description="エラーメッセージ")
    error_code: str = Field(default="GENERAL_ERROR", description="エラーコード")
    timestamp: datetime = Field(default_factory=datetime.now)


class ProgressResponse(BaseModel):
    """進捗レスポンスモデル"""

    progress: float = Field(..., ge=0, le=100, description="進捗率（%）")
    status: Literal["running", "complete", "error"] = Field(
        ..., description="ステータス"
    )
    pattern: Optional[List[int]] = Field(None, description="現在処理中のパターン")
    error: Optional[str] = Field(None, description="エラーメッセージ")
    results: Optional[AnalysisResult] = Field(None, description="完了時の結果")
