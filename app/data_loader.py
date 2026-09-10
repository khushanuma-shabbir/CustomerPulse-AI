from app.supabase_client import supabase
import pandas as pd


def load_tickets():
    response = supabase.table("tickets").select("*").execute()

    df = pd.DataFrame(response.data)

    print("Dataset loaded successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    return df


if __name__ == "__main__":
    df = load_tickets()

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())