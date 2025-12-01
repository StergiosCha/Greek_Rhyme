import json

with open("rhyme_corpus.json", "r") as f:
    corpus = json.load(f)

found = False
for poet, data in corpus.items():
    for ex in data['examples']:
        l1 = ex['lines'][0]
        l2 = ex['lines'][1]
        
        # Check ftera/kalivi mas
        if "φτερά" in l1 and "καλύβι μας" in l2:
            print(f"FOUND: {l1} / {l2}")
            print(f"Class: {ex['classification']}")
            print(f"Phonetic: {ex['phonetic']}")
            found = True
            
        # Check pisti/xario (just in case)
        if "πιστ" in l1 and "χαρι" in l2:
             # print(f"POTENTIAL PISTI: {l1} / {l2}")
             pass

if not found:
    print("ftera/kalivi mas NOT FOUND in corpus.")
