from greek_phonology import get_possible_syllable_counts

words = ["ιά", "παιδιά", "τέτοιος"]

for w in words:
    print(f"Word: {w}")
    counts = get_possible_syllable_counts(w)
    print(f"  Counts: {counts}")
    print("-" * 20)
