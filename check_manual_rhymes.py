from greek_phonology import classify_rhyme_pair

# Check manually
pairs = [
    ("πουλάκια", "τζάκια"),  # Lines 1,3
    ("όξω", "όξω"),  # Lines 2,5
    ("όξω", "βιτρολώξω"),  # Lines 2,6
    ("µουτράκι", "πουλάκια"),  # Lines 7,1
]

for w1, w2 in pairs:
    res = classify_rhyme_pair(w1, w2)
    print(f"'{w1}' vs '{w2}': {res['type']}")
