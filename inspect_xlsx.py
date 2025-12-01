import pandas as pd

try:
    df = pd.read_excel("GLC_Anemoskala_select_text.xlsx")
    print("Columns:", df.columns.tolist())
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())
    print("\nTotal rows:", len(df))
except Exception as e:
    print(f"Error reading excel: {e}")
