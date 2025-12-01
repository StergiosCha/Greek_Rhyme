from greek_phonology import classify_rhyme_pair, get_rhyme_part_and_onset

w1 = "ιδώ"
w2 = "κορμί"

print(f"Testing {w1} vs {w2}")
rp1, on1 = get_rhyme_part_and_onset(w1)
rp2, on2 = get_rhyme_part_and_onset(w2)
print(f"  {w1}: RP='{rp1}', Onset='{on1}'")
print(f"  {w2}: RP='{rp2}', Onset='{on2}'")

res = classify_rhyme_pair(w1, w2)
print(f"Result: {res}")
