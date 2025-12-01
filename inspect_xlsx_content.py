import pandas as pd
import re

def clean_html(raw_html):
    if not isinstance(raw_html, str):
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

try:
    df = pd.read_excel("GLC_Anemoskala_select_text.xlsx")
    
    # Filter for rows that look like verses (not headers)
    # Heuristic: HTML doesn't start with <h1, <div class="ab" (date?)
    # Or just clean everything and see.
    
    print("Sample cleaned lines:")
    count = 0
    for idx, row in df.iterrows():
        text = clean_html(row['html'])
        if text and len(text) > 5 and count < 20:
            print(f"Work: {row['work']} | Text: {text}")
            count += 1
            
    print("\nUnique Works:", df['work'].nunique())
    print("Sample Works:", df['work'].unique()[:10])
    
except Exception as e:
    print(f"Error: {e}")
