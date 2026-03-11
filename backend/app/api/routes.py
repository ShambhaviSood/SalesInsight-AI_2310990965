"""API route definitions."""

import logging

from fastapi import APIRouter, File, Form, Request, UploadFile, HTTPException, status

from app.core.config import get_settings
from app.core.security import (
    get_client_ip,
    rate_limiter,
    sanitize_email,
    validate_upload_file,
)
from app.models.schemas import ChartData, ErrorResponse, HealthResponse, SummaryResponse
from app.services.ai_engine import generate_summary
from app.services.email_service import send_summary_email
from app.services.file_processor import parse_sales_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
)
async def health_check():
    settings = get_settings()
    return HealthResponse(status="healthy", version=settings.APP_VERSION)


@router.post(
    "/upload",
    response_model=SummaryResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Sales"],
    summary="Upload sales data and receive an AI-generated executive summary via email",
    description=(
        "Upload a CSV or Excel file containing sales data along with a recipient "
        "email. The system parses the data, generates an AI executive summary, "
        "and emails it to the specified address."
    ),
)
async def upload_and_summarize(
    request: Request,
    file: UploadFile = File(..., description="Sales data file (.csv, .xlsx, .xls)"),
    recipient_email: str = Form(..., description="Email address to send the summary"),
):
    # Rate limiting
    client_ip = get_client_ip(request)
    rate_limiter.check(client_ip)

    # Sanitize email
    email = sanitize_email(recipient_email)

    # Validate file
    file_bytes = await validate_upload_file(file)

    logger.info(
        "Processing upload: file=%s size=%d email=%s ip=%s",
        file.filename,
        len(file_bytes),
        email,
        client_ip,
    )

    # Step 1: Parse sales data
    try:
        parsed_data = parse_sales_data(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Step 2: Generate AI summary
    try:
        summary = await generate_summary(parsed_data)
    except Exception as e:
        logger.error("AI summary generation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI summary: {e}",
        )

    # Step 3: Send email
    email_sent = False
    try:
        await send_summary_email(email, summary)
        email_sent = True
    except Exception as e:
        logger.error("Email delivery failed: %s", e, exc_info=True)

    if email_sent:
        message = f"Executive summary generated and emailed to {email}."
    else:
        message = (
            f"Executive summary generated successfully, but email delivery to {email} failed. "
            "You can view the summary below. Please check your email settings or try again."
        )

    # Build chart data from parsed stats
    stats = parsed_data.get("stats", {})
    chart_data = ChartData(
        primary_total=stats.get("primary_total", 0),
        primary_numeric_col=stats.get("primary_numeric_col", ""),
        breakdowns=stats.get("breakdowns", {}),
        numeric_summary=stats.get("numeric_summary", {}),
        total_revenue=stats.get("total_revenue", 0),
        revenue_by_region=stats.get("revenue_by_region", {}),
        revenue_by_product=stats.get("revenue_by_product", {}),
    )

    return SummaryResponse(
        success=True,
        message=message,
        summary=summary,
        chart_data=chart_data,
    )
