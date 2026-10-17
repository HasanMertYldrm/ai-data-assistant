import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:

    column_profiles = []

    for column in df.columns:

        series = df[column]

        missing_count = int(series.isna().sum())

        whitespace_count = int(
            series.map(
                lambda value: isinstance(value, str)
                and value.strip() == ""
            ).sum()
        )

        column_profiles.append({
            "column": column,
            "dtype": str(series.dtype),
            "missing_values": missing_count,
            "whitespace_only": whitespace_count
        })

    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": column_profiles
    }

    return profile