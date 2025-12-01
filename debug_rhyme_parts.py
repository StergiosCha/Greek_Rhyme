from greek_phonology import get_rhyme_part_and_onset, g2p_greek

w1 = "στάσου"
w2 = "μαλλιά σου"

print(f"Word 1: {w1}")
print(f"  Phonetic: {g2p_greek(w1)}")
rp1, on1 = get_rhyme_part_and_onset(w1)
print(f"  Rhyme Part: '{rp1}'")
print(f"  Onset: '{on1}'")

print(f"\nWord 2: {w2}")
print(f"  Phonetic: {g2p_greek(w2)}")
rp2, on2 = get_rhyme_part_and_onset(w2)
print(f"  Rhyme Part: '{rp2}'")
print(f"  Onset: '{on2}'")

print(f"\nMatch? {rp1} == {rp2}")
