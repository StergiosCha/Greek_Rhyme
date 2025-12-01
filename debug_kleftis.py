from greek_phonology import classify_rhyme_pair

# Test kleftis vs meni (IMP-0 false positive)
w1 = "κλέφτης" # kleftis -> eftis
w2 = "μένει"   # meni -> eni
print(f"Testing {w1} vs {w2}")
res = classify_rhyme_pair(w1, w2)
print(f"Result: {res}")

# Test valid IMP-0 (Consonant vs Zero)
# e.g. 'is' vs 'i'
w3 = "πίστης"
w4 = "πίστη"
print(f"Testing {w3} vs {w4}")
res2 = classify_rhyme_pair(w3, w4)
print(f"Result: {res2}")

# Test iDo vs kormi (IMP-V false positive)
w5 = "ιδώ" # iDo -> o
w6 = "κορμί" # kormi -> i
print(f"Testing {w5} vs {w6}")
res3 = classify_rhyme_pair(w5, w6)
print(f"Result: {res3}")
