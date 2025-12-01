from greek_phonology import get_rhyme_part_and_onset, g2p_greek

# Test g2p punctuation stripping
text = "δώρα,"
print(f"g2p('{text}') -> '{g2p_greek(text)}'")

# Test clitic stress
# "kalivi mas" -> Should be stressed on 'kalivi'
w = "καλύβι μας"
rp, on = get_rhyme_part_and_onset(w)
print(f"'{w}' -> RP: '{rp}', Onset: '{on}'")

# "ftera"
w2 = "φτερά"
rp2, on2 = get_rhyme_part_and_onset(w2)
print(f"'{w2}' -> RP: '{rp2}', Onset: '{on2}'")

# Check IMP-0 logic simulation
# If rp='as' and rp2='a' -> IMP-0?
