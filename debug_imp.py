from greek_phonology import classify_rhyme_pair

# Test IMP-0 (Consonant vs Zero)
# "pistis" (faith) vs "pisti" (faiths/faithful)
# Phonetic: [pi'stis] vs [pi'sti]
# Rhyme part: 'is' vs 'i'
# vs=['i'], vs=['i']. Match.
# cs=['s'], cs=[]. Mismatch (C vs Zero).
w1 = "πίστης" # pistis
w2 = "πίστη" # pisti

print(f"Testing {w1} vs {w2}")
res = classify_rhyme_pair(w1, w2)
print(f"Result: {res}")

# Test IMP-C (Place Match)
# "ksafnizi" (z) vs "texniti" (t)
w3 = "ξαφνίζει"
w4 = "τεχνίτη"
print(f"Testing {w3} vs {w4}")
res2 = classify_rhyme_pair(w3, w4)
print(f"Result: {res2}")
