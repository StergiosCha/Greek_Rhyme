from greek_phonology import extract_rhyme_domain, detect_stress_position, count_syllables

words = [
    "τέτοιος", # Synizesis candidate
    "ποιος",   # Synizesis candidate
    "παιδιά",  # Synizesis candidate
    "ωραία",   # Hiatus?
    "αηδόνι",  # Digraph?
    "καϊκι",   # Diaeresis
]

print(f"{'Word':<15} | {'Syllables':<10} | {'Stress':<10} | {'Rhyme Domain':<20} | {'Phonetic':<20}")
print("-" * 85)

for w in words:
    syll = count_syllables(w)
    stress = detect_stress_position(w)
    rd = extract_rhyme_domain(w)
    print(f"{w:<15} | {syll:<10} | {str(stress):<10} | {rd['rhyme_domain']:<20} | {rd['rhyme_domain_phonetic']:<20}")
