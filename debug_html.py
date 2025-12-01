import re
from greek_phonology import classify_rhyme_pair

def clean_html(raw_html):
    if not isinstance(raw_html, str):
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

text1 = "ψυχικό&nbsp;"
text2 = "εκεί&nbsp;"

clean1 = clean_html(text1)
clean2 = clean_html(text2)

print(f"Cleaned 1: '{clean1}'")
print(f"Cleaned 2: '{clean2}'")

res = classify_rhyme_pair(clean1, clean2)
print(f"Result: {res}")
