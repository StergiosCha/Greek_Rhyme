import json

with open("rhyme_corpus.json", "r") as f:
    corpus = json.load(f)

found = False
for poet, data in corpus.items():
    for ex in data['examples']:
        # Check for Tira vs TiriDa
        l1 = ex['lines'][0]
        l2 = ex['lines'][1]
        if "θύρα" in l1 and "θυρίδα" in l2:
            print(f"FOUND: {l1} / {l2}")
            print(f"Class: {ex['classification']}")
            found = True

if not found:
    print("NOT FOUND in corpus.")
