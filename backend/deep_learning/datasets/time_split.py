import pandas as pd
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TimeSplitter:
    """
    Guarantees strict Out-of-Time splitting. 
    Prevents future data leakage by strictly partitioning by datetime.
    No random CV is allowed here.
    """
    def __init__(self, time_col: str = "timestamp"):
        self.time_col = time_col

    def split_by_date(
        self, 
        df: pd.DataFrame, 
        val_start: str, 
        test_start: str,
        train_start: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Splits data into train, val, test based on date strings (YYYY-MM-DD).
        """
        if self.time_col not in df.columns:
            raise ValueError(f"Time column '{self.time_col}' not found in dataframe.")
            
        df[self.time_col] = pd.to_datetime(df[self.time_col])
        val_start_dt = pd.to_datetime(val_start)
        test_start_dt = pd.to_datetime(test_start)
        
        # Train
        train_mask = df[self.time_col] < val_start_dt
        if train_start:
            train_start_dt = pd.to_datetime(train_start)
            train_mask = train_mask & (df[self.time_col] >= train_start_dt)
        train_df = df[train_mask].copy()
        
        # Validation
        val_mask = (df[self.time_col] >= val_start_dt) & (df[self.time_col] < test_start_dt)
        val_df = df[val_mask].copy()
        
        # Test
        test_mask = df[self.time_col] >= test_start_dt
        test_df = df[test_mask].copy()
        
        logger.info(f"OOT Split Complete -> Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        # Guard against leakage
        assert train_df[self.time_col].max() < val_df[self.time_col].min(), "Leakage detected between train and val"
        assert val_df[self.time_col].max() < test_df[self.time_col].min(), "Leakage detected between val and test"
        
        return train_df, val_df, test_df
