from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw/hotel_bookings.csv")
OUTPUT_PATH = Path("data/processed/hotel_bookings_clean.parquet")


def load_data(file_path: Path) -> pd.DataFrame:
    """Load the raw hotel bookings dataset."""
    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {file_path}")

    return pd.read_csv(file_path)


def clean_hotel_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform the hotel bookings dataset.

    Key decisions:
    - Each row is one booking.
    - Canceled and No-Show are treated as cancelled bookings.
    - Zero-night bookings are retained for cancellation analysis.
    - Records with zero total guests are excluded.
    - Negative ADR values are excluded.
    """

    df = df.copy()

    # ------------------------------------------------------------------
    # 1. Missing values
    # ------------------------------------------------------------------

    # Only four bookings have missing children values.
    df["children"] = df["children"].fillna(0).astype(int)

    # Replace adults with 1 where there are children or babies but no adults.
    condition = (df["adults"] == 0) & ((df["children"] > 0) | (df["babies"] > 0))
    df.loc[condition, "adults"] = 1

    # Missing country is retained as an explicit unknown category.
    df["country"] = df["country"].fillna("Unknown")

    # Agent/company missingness is meaningful, so preserve the IDs
    # and create explicit indicators.
    df["has_agent"] = df["agent"].notna()
    df["has_company"] = df["company"].notna()

    # ------------------------------------------------------------------
    # 2. Derived booking attributes
    # ------------------------------------------------------------------
    
    # Total guest is the sum of adults, children, and babies.
    df["total_guests"] = (
        df["adults"]
        + df["children"]
        + df["babies"]
    )

    # Total nights is the sum of weekend and week nights.
    df["total_nights"] = (
        df["stays_in_weekend_nights"]
        + df["stays_in_week_nights"]
    )

    # a booking is cancelled when its status is Canceled or No-Show.
    df["cancelled"] = df["reservation_status"].isin(
        ["Canceled", "No-Show"]
    )
    df.cancelled.value_counts()
    # ------------------------------------------------------------------
    # 3. Date transformations
    # ------------------------------------------------------------------

    month_map = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

    # Create an arrival_date column from the year, month, and day columns.
    df["arrival_date"] = pd.to_datetime(
        {
            "year": df["arrival_date_year"],
            "month": df["arrival_date_month"].map(month_map),
            "day": df["arrival_date_day_of_month"],
        }
    )

    # Convert the reservation_status_date column to datetime.
    df["reservation_status_date"] = pd.to_datetime(
        df["reservation_status_date"]
    )

    # ------------------------------------------------------------------
    # 4. Clearly invalid records
    # ------------------------------------------------------------------

    # The booking should have at least one adult (one guest). So exclude records with zero total guests.
    df = df[(df["total_guests"] > 0) & (df["adults"] > 0)]

    # Negative ADR is not a meaningful room rate.
    df = df[df["adr"] >= 0]

    # ------------------------------------------------------------------
    # 5. Final dataframe
    # ------------------------------------------------------------------

    return df.reset_index(drop=True)


def save_data(df: pd.DataFrame, output_path: Path) -> None:
    """Save the processed dataset as Parquet."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"Processed dataset saved to: {output_path}")


def main() -> None:
    print(f"Loading raw data from: {RAW_PATH}")

    df_raw = load_data(RAW_PATH)

    print(f"Raw shape:       {df_raw.shape}")

    df_clean = clean_hotel_data(df_raw)

    print(f"Processed shape: {df_clean.shape}")
    print(f"Rows removed:    {len(df_raw) - len(df_clean):,}")

    save_data(df_clean, OUTPUT_PATH)


if __name__ == "__main__":
    main()