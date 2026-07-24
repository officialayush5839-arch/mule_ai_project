import pandas as pd

class TemporalFeatureExtractor:
    """
    Extracts time-based and velocity features from transaction histories.
    """
    @staticmethod
    def extract_features(df: pd.DataFrame, time_col: str = "timestamp") -> pd.DataFrame:
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])
        
        # Base Time Features
        df["hour"] = df[time_col].dt.hour
        df["day_of_week"] = df[time_col].dt.dayofweek
        df["month"] = df[time_col].dt.month
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        
        # Velocity Features (Mocked for batch calculation)
        # In production, these are calculated over rolling windows per entity.
        df["rolling_mean_7d"] = df["amount"].rolling(window=7, min_periods=1).mean()
        df["rolling_std_7d"] = df["amount"].rolling(window=7, min_periods=1).std().fillna(0)
        df["transaction_count_last_7d"] = df["amount"].rolling(window=7, min_periods=1).count()
        
        return df
