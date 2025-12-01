from greek_phonology import classify_rhyme_pair

# Test overwrite issue
w1 = "κλέφτης" # F2
w2 = "ψεύτης" # F2
print(f"Testing {w1} vs {w2} (Pure F2)")
res = classify_rhyme_pair(w1, w2)
print(f"Result: {res}")

w3 = "ξαφνίζει" # F2
w4 = "τεχνίτη" # F2 (IMP-C)
print(f"Testing {w3} vs {w4} (IMP-C F2)")
res2 = classify_rhyme_pair(w3, w4)
print(f"Result: {res2}")
