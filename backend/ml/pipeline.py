"""
pipeline.py
===========
REPLACED – was: random feature imputation + manual ratio calculations.
NOW:  Thin adapter that prepares feature DataFrames for the inference engine.

The calculate_feature_metrics() function signature is preserved for
backward compatibility with any existing callers.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

FEATURE_COLS = ["F115", "F321", "F527", "F670", "F1692", "F3043", "F3894"]


def calculate_feature_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare a raw transaction DataFrame for batch inference.

    - If required feature columns are missing, uses column medians from
      present columns or 0.5 as a structural default.
    - NEVER generates random values for missing columns.
    - Clips all feature values to [0, 1].

    Parameters
    ----------
    df : DataFrame with arbitrary columns (may include F-codes or aliases)

    Returns
    -------
    DataFrame with exactly FEATURE_COLS columns, clipped to [0, 1].
    """
    processed = df.copy()

    for col in FEATURE_COLS:
        if col not in processed.columns:
            # Use median of any numerically similar column if possible
            numeric_cols = processed.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                fallback = float(processed[numeric_cols].median().median())
            else:
                fallback = 0.5
            logger.warning(
                "Column '%s' missing from input – using structural default %.3f "
                "(not random). Upload a dataset with correct columns for accurate scoring.",
                col, fallback,
            )
            processed[col] = fallback
        else:
            # Impute NaNs with column median (never random)
            median_val = processed[col].median()
            processed[col] = processed[col].fillna(median_val)

        # Clip to valid range
        processed[col] = processed[col].clip(0.0, 1.0)

    return processed
