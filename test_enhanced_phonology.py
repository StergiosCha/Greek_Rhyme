from greek_phonology import classify_rhyme_pair, syllabify

pairs = [
    ("παιδιά", "καρδιά"), # Pure M
    ("κρίνα", "ελαφίνα"), # Pure F2 (or Rich if onsets match? kr vs l. No)
    ("στόματα", "σώματα"), # Pure F3? No, s-t vs s. Pure F3.
    ("καλά", "χαλά"), # Rich? k vs x. No.
    # Rich Rhyme examples from paper:
    # "αλισωμένο" - "γραμμένο" (TR-S? aliso-meno vs gram-meno. m vs m. Yes)
    ("αλισωμένο", "γραμμένο"),
    # "αυγή" - "ναυγή" (TR-CC? avji vs navji. vji vs vji. Yes)
    ("αυγή", "ναυγή"),
    
    # Imperfect Rhymes
    ("χάνεται", "γίνεται"), # IMP-V? 'anete' vs 'inete'.
    ("ξαφνίζει", "τεχνίτη"), # IMP-C? 'izi' vs 'iti'.
    
    # Non-rhymes
    ("σπίτι", "δρόμος")
]

for w1, w2 in pairs:
    print(f"Pair: {w1} - {w2}")
    res = classify_rhyme_pair(w1, w2)
    print(f"  Result: {res}")
    print("-" * 20)
