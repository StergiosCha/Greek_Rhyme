import json

with open("rhyme_corpus.json", "r") as f:
    corpus = json.load(f)

print("Searching for IMP-0 rhymes...")
count = 0
for poet, data in corpus.items():
    for ex in data['examples']:
        if "IMP-0" in ex['features'] or "IMP-0" in ex['classification']:
            print(f"IMP-0: {ex['lines'][0]} / {ex['lines'][1]}")
            print(f"  Phonetic: {ex['phonetic']}")
            count += 1
            if count > 20: break
    if count > 20: break

print(f"Total IMP-0 found so far: {count}")
