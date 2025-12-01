from greek_phonology import classify_rhyme_pair

# Test the rhyme pairs from Claude's latest attempt (no RAG)
pairs = [
    ("γεννά", "σταματά"),      # Lines 1-3
    ("στιγμή", "ψυχή"),         # Lines 2-4
    ("γλυκά", "φωτιά"),         # Lines 5-7
    ("ουρανό", "σκοτεινό"),     # Lines 6-8
    ("μπροστά", "κρατά"),       # Lines 9-11
    ("μαζί", "νικά"),           # Lines 10-12
]

print("=== CLAUDE NO-RAG ATTEMPT - RHYME VERIFICATION ===\n")

valid_count = 0
for idx, (w1, w2) in enumerate(pairs, 1):
    result = classify_rhyme_pair(w1, w2)
    is_valid = result['type'] != 'NONE'
    if is_valid:
        valid_count += 1
    
    status = "✓" if is_valid else "✗"
    print(f"Pair {idx}: {status} {w1:15} / {w2:15} → {result['type']}", end="")
    if 'subtype' in result:
        print(f" ({result['subtype']})", end="")
    print()

print(f"\n✓ Valid pairs: {valid_count}/6 ({valid_count*100//6}%)")
