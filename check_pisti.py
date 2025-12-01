import json

with open("rhyme_corpus.json", "r") as f:
    corpus = json.load(f)

found = False
for poet, data in corpus.items():
    for ex in data['examples']:
        # Check for pisti/xario phonetic
        p1 = ex['phonetic'][0]
        p2 = ex['phonetic'][1]
        
        if ("pisti" in p1 and "xario" in p2) or ("xario" in p1 and "pisti" in p2):
            print(f"FOUND: {ex['lines'][0]} / {ex['lines'][1]}")
            print(f"Class: {ex['classification']}")
            print(f"Phonetic: {ex['phonetic']}")
            print(f"Details: {ex['features']}")
            found = True

if not found:
    print("NOT FOUND by phonetic. Checking Greek text...")
    for poet, data in corpus.items():
        for ex in data['examples']:
            l1 = ex['lines'][0]
            l2 = ex['lines'][1]
            if "πιστ" in l1 and "χαρι" in l2: # Broad search
                 print(f"POTENTIAL: {l1} / {l2}")
                 print(f"Phonetic: {ex['phonetic']}")
