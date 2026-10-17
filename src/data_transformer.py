import pandas as pd


def normalize_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace(r"^\s*$", pd.NA, regex=True)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(ignore_index=True)


def apply_operations(
    df: pd.DataFrame,
    operations: list[str]
) -> pd.DataFrame:

    result = df.copy(deep=True)

    for operation in operations:

        if operation == "normalize_whitespace":
            result = normalize_whitespace(result)

        elif operation == "remove_duplicates":
            result = remove_duplicates(result)

        else:
            raise ValueError(f"Unsupported operation: {operation}")

    return result