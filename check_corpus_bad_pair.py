import json

with open("rhyme_corpus.json", "r") as f:
    corpus = json.load(f)

found = False
for poet, data in corpus.items():
    for ex in data['examples']:
        # Check for psiXiko
        # Phonetic might be ['psiXiko', 'eki'] or similar
        # Or check lines
        l1 = ex['lines'][0]
        l2 = ex['lines'][1]
        if "ψυχικό" in l1 and "εκεί" in l2:
            print(f"FOUND: {l1} / {l2}")
            print(f"Class: {ex['classification']}")
            print(f"Phonetic: {ex['phonetic']}")
            found = True

if not found:
    print("NOT FOUND in corpus.")
