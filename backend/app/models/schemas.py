"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, EmailStr, Field


class UploadRequest(BaseModel):
    """Metadata accompanying the file upload."""
    recipient_email: EmailStr = Field(..., description="Email to send the summary to")


class ChartData(BaseModel):
    """Structured data for frontend chart rendering — works with any dataset."""
    primary_total: float = 0
    primary_numeric_col: str = ""
    breakdowns: dict[str, dict[str, float]] = Field(default_factory=dict, description="category_col -> {label: value}")
    numeric_summary: dict[str, dict[str, float]] = Field(default_factory=dict)
    # Legacy fields for sales-specific data
    total_revenue: float = 0
    revenue_by_region: dict[str, float] = Field(default_factory=dict)
    revenue_by_product: dict[str, float] = Field(default_factory=dict)


class SummaryResponse(BaseModel):
    """Response after successful summary generation and email delivery."""
    success: bool
    message: str
    summary: str = Field(default="", description="The generated executive summary")
    chart_data: ChartData = Field(default_factory=ChartData, description="Structured data for charts")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
