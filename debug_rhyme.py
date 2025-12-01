from greek_phonology import classify_rhyme_pair, get_possible_syllable_counts, detect_stress_position

w1 = "ψυχικό"
w2 = "εκεί"

print(f"Analyzing {w1} vs {w2}")
print(f"Stress {w1}: {detect_stress_position(w1)}")
print(f"Stress {w2}: {detect_stress_position(w2)}")

res = classify_rhyme_pair(w1, w2)
print(f"Result: {res}")

# Debug internal logic if possible, or just infer from result
