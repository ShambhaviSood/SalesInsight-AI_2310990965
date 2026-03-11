"""Sales data file processor using pandas."""

import io
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def parse_sales_data(file_bytes: bytes, filename: str) -> dict:
    """
    Parse CSV or Excel sales data and return structured analytics.

    Returns a dict with:
        - raw_text: string representation for LLM prompt
        - stats: computed summary statistics
    """
    ext = filename.rsplit(".", 1)[-1].lower()

    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError(f"Unsupported file extension: .{ext}")
    except Exception as e:
        logger.error("Failed to parse file %s: %s", filename, e)
        raise ValueError(f"Could not parse the uploaded file: {e}") from e

    if df.empty:
        raise ValueError("The uploaded file contains no data rows.")

    logger.info("Parsed %d rows x %d columns from %s", len(df), len(df.columns), filename)

    stats = _compute_stats(df)
    raw_text = _dataframe_to_text(df)

    return {"raw_text": raw_text, "stats": stats, "rows": len(df), "columns": list(df.columns)}


def _compute_stats(df: pd.DataFrame) -> dict:
    """Compute statistics from any tabular dataframe — fully generic."""
    stats: dict = {"row_count": len(df), "columns": list(df.columns)}

    # ── Numeric columns ──
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        stats["numeric_summary"] = {}
        for col in numeric_cols:
            col_data = df[col].dropna()
            if col_data.empty:
                continue
            stats["numeric_summary"][col] = {
                "sum": round(float(col_data.sum()), 2),
                "mean": round(float(col_data.mean()), 2),
                "min": round(float(col_data.min()), 2),
                "max": round(float(col_data.max()), 2),
            }

    # ── Categorical columns (for groupBy breakdowns) ──
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    # Exclude columns with too many unique values (likely IDs/names, not categories)
    cat_cols = [c for c in cat_cols if 1 < df[c].nunique() <= 30]

    # ── Pick the "primary numeric" column: prefer known names, else largest-sum numeric ──
    primary_num = _find_column(df, [
        "revenue", "total_revenue", "sales", "amount", "total", "profit",
        "price", "value", "cost", "income", "turnover",
    ])
    if not primary_num and numeric_cols:
        # Pick the numeric column with the highest sum (most likely the "value" column)
        primary_num = max(numeric_cols, key=lambda c: abs(df[c].sum()))

    if primary_num:
        stats["primary_numeric_col"] = primary_num
        stats["primary_total"] = round(float(df[primary_num].sum()), 2)

    # ── Generate breakdowns: group each categorical col by the primary numeric ──
    stats["breakdowns"] = {}
    if primary_num and cat_cols:
        for cat_col in cat_cols[:5]:  # limit to 5 most relevant categories
            grouped = df.groupby(cat_col)[primary_num].sum().sort_values(ascending=False)
            stats["breakdowns"][cat_col] = {
                str(k): round(float(v), 2) for k, v in grouped.head(15).items()
            }

    # ── Also generate breakdowns with secondary numeric columns ──
    stats["secondary_breakdowns"] = {}
    secondary_numerics = [c for c in numeric_cols if c != primary_num]
    if secondary_numerics and cat_cols:
        # Pick the first categorical and break down secondary numerics by it
        first_cat = cat_cols[0]
        for num_col in secondary_numerics[:3]:
            grouped = df.groupby(first_cat)[num_col].sum().sort_values(ascending=False)
            stats["secondary_breakdowns"][f"{num_col}_by_{first_cat}"] = {
                str(k): round(float(v), 2) for k, v in grouped.head(15).items()
            }

    # ── Legacy fields for backward compat (sales-specific) ──
    revenue_col = _find_column(df, ["revenue", "total_revenue", "sales", "amount"])
    region_col = _find_column(df, ["region", "area", "territory", "location"])
    product_col = _find_column(df, ["product", "product_category", "category", "item"])

    if revenue_col and region_col:
        stats["revenue_by_region"] = stats["breakdowns"].get(region_col, {})
    if revenue_col and product_col:
        stats["revenue_by_product"] = stats["breakdowns"].get(product_col, {})
    if revenue_col:
        stats["total_revenue"] = round(float(df[revenue_col].sum()), 2)

    return stats


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Find the first matching column name (case-insensitive)."""
    col_lower = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in col_lower:
            return col_lower[candidate.lower()]
    return None


def _dataframe_to_text(df: pd.DataFrame, max_rows: int = 20) -> str:
    """Convert dataframe to a text representation suitable for LLM context."""
    if len(df) > max_rows:
        sample = df.head(max_rows)
        suffix = f"\n... ({len(df) - max_rows} more rows truncated)"
    else:
        sample = df
        suffix = ""

    return sample.to_string(index=False) + suffix
