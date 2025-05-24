"""データモデルモジュール"""
from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, validator


class FortuneRequest(BaseModel):
    """姓名判断リクエストモデル"""
    last_name: str = Field(..., min_length=1, max_length=10, description="姓")
    first_name: str = Field(..., min_length=1, max_length=10, description="名")
    gender: Literal["m", "f"] = Field(..., description="性別")
    
    @validator("last_name", "first_name")
    def validate_japanese_characters(cls, v):
        """日本語文字の検証"""
        if not v.strip():
            raise ValueError("空文字は許可されていません")
        return v.strip()


class StrokeAnalysisRequest(BaseModel):
    """画数分析リクエストモデル"""
    last_name: str = Field(..., min_length=1, max_length=10, description="姓")
    char_count: int = Field(..., ge=1, le=3, description="文字数")


class NameCandidateRequest(BaseModel):
    """名前候補リクエストモデル"""
    chars: int = Field(..., ge=1, le=3, description="文字数")
    strokes_1: int = Field(..., ge=1, le=30, description="1文字目の画数")
    strokes_2: Optional[int] = Field(None, ge=1, le=30, description="2文字目の画数")
    strokes_3: Optional[int] = Field(None, ge=1, le=30, description="3文字目の画数")
    gender: Optional[Literal["male", "female", "unisex"]] = Field(None, description="性別")
    
    @validator("strokes_2")
    def validate_strokes_2(cls, v, values):
        """2文字目の画数検証"""
        if values.get("chars", 0) >= 2 and v is None:
            raise ValueError("2文字以上の場合、2文字目の画数は必須です")
        return v
    
    @validator("strokes_3")
    def validate_strokes_3(cls, v, values):
        """3文字目の画数検証"""
        if values.get("chars", 0) == 3 and v is None:
            raise ValueError("3文字の場合、3文字目の画数は必須です")
        return v


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
    top_results: List[StrokePattern] = Field(..., max_items=20)


class NameCandidate(BaseModel):
    """名前候補モデル"""
    name: str = Field(..., description="名前（漢字）")
    yomi: Optional[str] = Field(None, description="読み方")
    chars: int = Field(..., ge=1, le=3, description="文字数")
    strokes_1: int = Field(..., ge=1, le=30, description="1文字目の画数")
    strokes_2: Optional[int] = Field(None, ge=1, le=30, description="2文字目の画数")
    strokes_3: Optional[int] = Field(None, ge=1, le=30, description="3文字目の画数")
    total_strokes: int = Field(..., ge=1, le=90, description="総画数")
    gender: str = Field(..., description="性別")


class NameCandidateResponse(BaseModel):
    """名前候補レスポンスモデル"""
    candidates: List[NameCandidate] = Field(..., max_items=50)
    total_count: int = Field(..., ge=0, description="条件に合致した総数")


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル"""
    error: str = Field(..., description="エラーメッセージ")
    error_code: Optional[str] = Field(None, description="エラーコード")
    timestamp: datetime = Field(default_factory=datetime.now)


class ProgressResponse(BaseModel):
    """進捗レスポンスモデル"""
    progress: float = Field(..., ge=0, le=100, description="進捗率（%）")
    status: Literal["running", "complete", "error"] = Field(..., description="ステータス")
    pattern: Optional[List[int]] = Field(None, description="現在処理中のパターン")
    error: Optional[str] = Field(None, description="エラーメッセージ")
    results: Optional[AnalysisResult] = Field(None, description="完了時の結果") 