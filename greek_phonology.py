"""
Greek Phonology Module - G2P and Phonetic Analysis
Handles orthography-to-phonology mapping with special focus on MOSAIC rhymes
"""

import re
import unicodedata
from typing import List, Tuple, Dict

# Greek orthography to IPA/SAMPA mapping
# Greek orthography to IPA/SAMPA mapping
# "Diphthongs" are treated as Digraphs (monophthongs) or V+C sequences
DIGRAPHS_VOWELS = {
    # Iotacism - all map to [i]
    'ει': 'i', 'εί': 'i', 'οι': 'i', 'οί': 'i', 'υι': 'i', 'υί': 'i',
    # Other digraphs
    'αι': 'e', 'αί': 'e', 'ου': 'u', 'ού': 'u',
}

# Vowel-Consonant sequences (formerly "diphthongs")
# These are context sensitive: [av/af], [ev/ef]
VC_SEQUENCES = {
    'αυ': {'voiced': 'av', 'voiceless': 'af'},
    'αύ': {'voiced': 'av', 'voiceless': 'af'},
    'ευ': {'voiced': 'ev', 'voiceless': 'ef'},
    'εύ': {'voiced': 'ev', 'voiceless': 'ef'},
    'ηυ': {'voiced': 'iv', 'voiceless': 'if'}, 
    'ηύ': {'voiced': 'iv', 'voiceless': 'if'},
}

VOWELS_SINGLE = {
    'η': 'i', 'ι': 'i', 'υ': 'i',
    'ε': 'e', 'ο': 'o', 'ω': 'o',
    'α': 'a',
    # Accented singles
    'ή': 'i', 'ί': 'i', 'ύ': 'i',
    'έ': 'e', 'ό': 'o', 'ώ': 'o',
    'ά': 'a',
    # Diaeresis
    'ϊ': 'i', 'ϋ': 'i',
    'ΐ': 'i', 'ΰ': 'i',
}

CONSONANT_MAPPINGS = {
    'β': 'v', 'γ': 'ɣ', 'δ': 'ð', 'ζ': 'z', 'θ': 'θ',
    'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'ks',
    'π': 'p', 'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't',
    'φ': 'f', 'χ': 'x', 'ψ': 'ps',
    # Digraphs
    'μπ': 'b', 'ντ': 'd', 'γκ': 'g', 'γγ': 'ŋg',
    'τσ': 'ts', 'τζ': 'dz',
}

# Voiceless consonants that trigger /af/, /ef/
VOICELESS_CONSONANTS = {'θ', 'κ', 'ξ', 'π', 'σ', 'ς', 'τ', 'φ', 'χ', 'ψ'}

# ASCII-based phonetic notation (NOT IPA - better for LLMs)
ASCII_PHONETIC = {
    'θ': 'T', 'ð': 'D', 'ɣ': 'G', 'x': 'X',
    'ŋ': 'N', 'ʝ': 'J',
}

def g2p_greek(text: str, ascii_mode: bool = True) -> str:
    """
    Convert Greek orthography to phonetic transcription
    
    Args:
        text: Greek text input
        ascii_mode: Use ASCII phonetics (T/D/G) instead of IPA (θ/ð/ɣ)
    
    Returns:
        Phonetic transcription
    """
    text = unicodedata.normalize('NFC', text.lower().strip())
    # Remove punctuation (keep spaces)
    # Punctuation to remove: . , ; : ! ? - ' " ( ) [ ]
    # Keep Greek accents!
    import string
    # Greek punctuation: ; (question mark), . (period), , (comma), · (semicolon equivalent)
    # Also remove common symbols
    remove_chars = string.punctuation + "«»…—–"
    # Be careful not to remove accented chars if they are somehow considered punctuation (unlikely)
    
    # We want to keep spaces for word boundaries if needed, but g2p usually processes words?
    # If input is a phrase, we keep spaces.
    
    cleaned_text = ""
    for c in text:
        if c not in remove_chars:
            cleaned_text += c
            
    text = cleaned_text
    phonetic = ""
    i = 0
    
    while i < len(text):
        # Check digraphs first (2-3 characters)
        matched = False
        
        # Check 2-char sequences
        if i + 2 <= len(text):
            substr = text[i:i+2]
            
            # Check Vowel Digraphs (Monophthongs)
            if substr in DIGRAPHS_VOWELS:
                phonetic += DIGRAPHS_VOWELS[substr]
                i += 2
                continue
            
            # Check V+C Sequences (αυ, ευ)
            if substr in VC_SEQUENCES:
                # Look ahead for next char to determine voicing
                next_char = text[i+2] if i + 2 < len(text) else '#' # # is end of word
                is_voiceless = next_char in VOICELESS_CONSONANTS or next_char == '#'
                
                mapping = VC_SEQUENCES[substr]
                phonetic += mapping['voiceless'] if is_voiceless else mapping['voiced']
                i += 2
                continue
            
            # Check Consonant Digraphs
            if substr in CONSONANT_MAPPINGS:
                phonetic += CONSONANT_MAPPINGS[substr]
                i += 2
                continue
        
        # Single character
        char = text[i]
        if char in VOWELS_SINGLE:
            # Check for Synizesis (unstressed i + Vowel)
            # This is complex to do perfectly without stress info here, 
            # but we can do a basic check if we assume input might have accents
            # For now, simple mapping, synizesis handled in syllabification or separate pass
            phonetic += VOWELS_SINGLE[char]
        elif char in CONSONANT_MAPPINGS:
            phonetic += CONSONANT_MAPPINGS[char]
        elif char == ' ':
            phonetic += ' '
        elif char in '.,;!?':
            pass  # Skip punctuation
        else:
            phonetic += char
        
        i += 1
    
    # Convert to ASCII phonetics if requested
    if ascii_mode:
        for ipa, ascii_rep in ASCII_PHONETIC.items():
            phonetic = phonetic.replace(ipa, ascii_rep)
    
    return phonetic


# Consonant Features for IMP-C checking
# Format: 'char': (Place, Manner)
# Place: 1=Labial, 2=Dental/Alveolar, 3=Velar/Palatal
# Manner: 1=Stop, 2=Fricative, 3=Nasal, 4=Liquid
CONSONANT_FEATURES = {
    'p': (1, 1), 'b': (1, 1), 'f': (1, 2), 'v': (1, 2), 'm': (1, 3),
    't': (2, 1), 'd': (2, 1), 'T': (2, 2), 'D': (2, 2), 's': (2, 2), 'z': (2, 2), 'n': (2, 3), 'l': (2, 4), 'r': (2, 4),
    'k': (3, 1), 'g': (3, 1), 'x': (3, 2), 'G': (3, 2)
}

def detect_stress_position(word: str) -> List[Tuple[int, str]]:
    """
    Detect stress position in Greek word.
    Returns a LIST of possible classifications due to flexible syllabification.
    Each item is (syllable_from_end, classification).
    
    e.g. 'τέτοιος' -> [(2, 'F2'), (3, 'F3')] (if synizesis applies or not)
    """
    word = unicodedata.normalize('NFC', word)
    
    # Find accent marks
    accent_chars = 'άέήίόύώ'
    
    # Locate stressed syllable (character index)
    stress_pos = -1
    for i, char in enumerate(word):
        if char in accent_chars:
            stress_pos = i
            break
    
    # If no accent found
    if stress_pos == -1:
        # Assume paroxytone for multi-syllable, oxytone for monosyllable
        # But now we have multiple counts!
        counts = get_possible_syllable_counts(word)
        results = set()
        for c in counts:
            if c == 1:
                results.add((1, 'M'))
            else:
                results.add((2, 'F2'))
        return sorted(list(results))
    
    # Count syllables after stress
    after_stress = word[stress_pos:]
    # syllables_after = count_syllables(after_stress) - 1
    
    # Now we get a SET of possible counts for the suffix
    suffix_counts = get_possible_syllable_counts(after_stress)
    
    results = set()
    for sc in suffix_counts:
        syllables_after = sc - 1
        
        if syllables_after == 0:
            results.add((1, 'M'))
        elif syllables_after == 1:
            results.add((2, 'F2'))
        else:
            results.add((3, 'F3'))
            
    return sorted(list(results), key=lambda x: x[0])
    # print(f"DEBUG: word={word}, stress_pos={stress_pos}, after_stress={after_stress}, count={count_syllables(after_stress)}, syllables_after={syllables_after}")
    
    if syllables_after == 0:
        return (1, 'M')  # Oxytone
    elif syllables_after == 1:
        return (2, 'F2')  # Paroxytone
    else:
        return (3, 'F3')  # Proparoxytone

def get_possible_syllable_counts(text: str) -> set[int]:
    """
    Get all possible syllable counts for a word, considering:
    1. Synizesis (standard): Unstressed /i/ + V = 1 syllable
    2. Diaeresis (poetic): Unstressed /i/ + V = 2 syllables
    
    Returns a set of possible counts (e.g., {2, 3} for 'τέτοιος')
    """
    text = unicodedata.normalize('NFC', text.lower())
    
    # Pass 1: Tokenize into "Vowel Units" (Digraphs, V+C, Single Vowels) and Consonants
    units = []
    idx = 0
    
    # Vowels that can be nuclei
    VOWELS = set('αεηιουωάέήίόύώϊϋΐΰ')
    
    while idx < len(text):
        # Digraphs
        if idx + 2 <= len(text) and text[idx:idx+2] in DIGRAPHS_VOWELS:
            units.append({'type': 'V', 'text': text[idx:idx+2], 'sound': DIGRAPHS_VOWELS[text[idx:idx+2]]})
            idx += 2
            continue
        # V+C
        if idx + 2 <= len(text) and text[idx:idx+2] in VC_SEQUENCES:
            units.append({'type': 'V', 'text': text[idx:idx+2], 'sound': 'V'}) # Treat as V nucleus
            idx += 2
            continue
        # Single Vowel
        if text[idx] in VOWELS:
            sound = VOWELS_SINGLE.get(text[idx], 'V')
            units.append({'type': 'V', 'text': text[idx], 'sound': sound})
            idx += 1
            continue
        # Consonant
        units.append({'type': 'C', 'text': text[idx]})
        idx += 1
        
    # Calculate counts
    # We will count "synizesis opportunities"
    
    base_nuclei = 0
    synizesis_opportunities = 0
    
    u = 0
    while u < len(units):
        unit = units[u]
        
        if unit['type'] == 'V':
            base_nuclei += 1
            
            # Check for Synizesis condition
            # 1. Is it /i/ sound?
            is_i = unit['sound'] == 'i'
            # 2. Is it unstressed? (No accent mark)
            is_unstressed = not any(ac in unit['text'] for ac in 'άέήίόύώΐΰ')
            
            # 3. Is the NEXT unit a Vowel?
            has_next_vowel = False
            if u + 1 < len(units) and units[u+1]['type'] == 'V':
                has_next_vowel = True
            
            if is_i and is_unstressed and has_next_vowel:
                # This is a synizesis opportunity.
                # If we apply synizesis, this nucleus merges with the next one (count -1)
                # But wait, if we have i-i-a? 
                # Let's assume synizesis affects the CURRENT unit (becoming a glide).
                # So if we apply it, we DON'T count this as a nucleus.
                # But we already incremented base_nuclei.
                synizesis_opportunities += 1
        
        u += 1
        
    # If we have N synizesis opportunities, we can have anywhere from 0 to N applications.
    # Max syllables = base_nuclei (0 synizesis applied, i.e., full Diaeresis)
    # Min syllables = base_nuclei - synizesis_opportunities (All synizesis applied)
    
    # However, we should be careful about overlapping opportunities?
    # e.g. i-i-a. 
    # Unit 1 (i): Unstressed, next is V(i). Opportunity.
    # Unit 2 (i): Unstressed, next is V(a). Opportunity.
    # If we apply Synizesis to 1: it becomes glide. Unit 2 is nucleus.
    # Can Unit 2 ALSO be a glide for Unit 3? /jja/? 
    # Usually yes. 'bja' (bia). 'iia'? 
    # Let's assume independent opportunities for now, or just return the range.
    
    max_count = max(base_nuclei, 1)
    min_count = max(base_nuclei - synizesis_opportunities, 1)
    
    return set(range(min_count, max_count + 1))

def count_syllables(text: str) -> int:
    """
    Count syllables. Returns the MINIMUM count (standard Synizesis).
    Use get_possible_syllable_counts for full flexibility.
    """
    counts = get_possible_syllable_counts(text)
    return min(counts)

def extract_rhyme_domain(line: str, include_context: bool = False) -> Dict:
    """
    Extract rhyme domain from line-final position
    
    For MOSAIC detection, we need to handle word boundaries specially
    
    Args:
        line: Greek text line
        include_context: Include pre-rhyme context for IDV detection
    
    Returns:
        Dict with rhyme_domain, stress_type, words (for MOS detection)
    """
    # Strip all common punctuation marks from end of line
    # Added: · (Greek ano teleia), • (Bullet), and others
    line = line.strip().rstrip('.,;!?:–—""«»\'"()[]…-·•')
    words = line.split()
    
    if not words:
        return {'rhyme_domain': '', 'stress_type': 'M', 'words': [], 'rhyme_domain_phonetic': '', 'is_potential_mosaic': False}
    
    last_word = words[-1]
    stress_options = detect_stress_position(last_word)
    
    # Default to the first option (usually the one with FEWEST syllables -> Synizesis applied -> Lower index)
    # Wait, detect_stress_position sorts by index (1, 2, 3).
    # 1=M, 2=F2, 3=F3.
    # If we have Synizesis, we have FEWER syllables.
    # e.g. 'τέτοιος'.
    # Synizesis: 2 syllables. Stress on 1st. Syllables after = 1. -> F2.
    # Diaeresis: 3 syllables. Stress on 1st. Syllables after = 2. -> F3.
    # So F2 < F3.
    # We want to support BOTH?
    # For now, let's pick the primary one (F2 / Synizesis) as default, but return all.
    
    primary_stress = stress_options[0] # (pos, type)
    stress_pos, stress_type = primary_stress
    
    # Extract rhyme domain based on PRIMARY stress
    # Check for Clitics (Unstressed final words)
    # If last word has NO accent, it might be a clitic, so stress is on previous word.
    has_accent = any(c in 'άέήίόύώΐΰ' for c in last_word)
    
    rhyme_words = [last_word]
    rhyme_domain = last_word
    
    if not has_accent and len(words) >= 2:
        # Last word is likely clitic (e.g. 'μου', 'της', 'το').
        # Look at previous word.
        prev_word = words[-2]
        # Check if prev_word has accent
        if any(c in 'άέήίόύώΐΰ' for c in prev_word):
            # Yes. The rhyme domain includes prev_word + last_word
            rhyme_words = [prev_word, last_word]
            rhyme_domain = f"{prev_word} {last_word}"
            
            # Re-calculate stress type for the PHRASE
            # This is tricky. We need to count syllables from the accent in prev_word to the end of phrase.
            # But for now, let's assume it's F2 or F3.
            # 'όνομά της' -> 'ma' is stressed. 'tis' follows. -> F2.
            # 'δωσε μου' -> 'do' stressed. 'se', 'mu' follow. -> F3.
            
            # Let's trust detect_stress_position on the PHRASE?
            # detect_stress_position takes a word.
            # Let's pass the phrase.
            stress_options = detect_stress_position(rhyme_domain)
            if stress_options:
                 primary_stress = stress_options[0]
                 stress_type = primary_stress[1]
            else:
                 # Fallback
                 stress_type = 'F2' # Most common for clitics
        else:
            # Both unstressed? Weird. Maybe 'μου το'?
            pass
            
    elif not has_accent:
        # Unstressed word but no previous word? (e.g. 'το')
        stress_type = 'M' # Treat as M
        
    else:
        # Last word HAS accent.
        # Standard case.
        # But wait, what about "o batis"? 'batis' has accent.
        # Is it mosaic? No, it's a single word rhyme 'batis'.
        # But Solomos rhymes "onoma tis" (F2) with "o batis" (F2).
        # "onoma tis" -> 'ma tis'.
        # "batis" -> 'ba tis'.
        # They rhyme!
        # So for "onoma tis", we correctly identified it as Mosaic F2.
        # For "batis", it is Standard F2.
        # My previous code forced "mosaic candidate" if len(words) > 1.
        # "o batis" -> words=["o", "batis"]. len=2. -> Forced Mosaic?
        # NO! We should only include previous word if it contributes to the rhyme domain (i.e. Clitic case).
        # OR if we are doing a "Rich Mosaic" check?
        # No, "o batis" is NOT a mosaic rhyme. It's a standard rhyme that rhymes WITH a mosaic.
        
        # So: Only extend rhyme_words if last_word is CLITIC.
        pass

    # Re-evaluate stress if we didn't change it (for standard case)
    if len(rhyme_words) == 1:
         # Use the already calculated stress_options for last_word
         pass
    
    # Convert to phonetics
    phonetic = g2p_greek(rhyme_domain, ascii_mode=True)
    
    result = {
        'rhyme_domain': rhyme_domain,
        'rhyme_domain_phonetic': phonetic,
        'stress_type': stress_type,
        'words': rhyme_words,
        'is_potential_mosaic': len(rhyme_words) > 1
    }
    
    if include_context and len(words) >= 2:
        # Include pre-rhyme word for IDV detection
        result['pre_rhyme_word'] = words[-2] if len(rhyme_words) == 1 else words[-3] if len(words) >= 3 else ""
    
    return result

def syllabify(word: str) -> List[str]:
    """
    Split word into phonetic syllables.
    Uses the 'Flexible' logic but defaults to Synizesis (min count) for segmentation.
    Returns list of phonetic syllables (e.g. 'παιδιά' -> ['pe', 'dja'])
    """
    # This is a simplified syllabification for rhyme analysis.
    # It relies on the Vowel Unit tokenization we built for counting.
    
    word = unicodedata.normalize('NFC', word.lower())
    
    # 1. Tokenize (reuse logic from get_possible_syllable_counts)
    units = []
    idx = 0
    VOWELS = set('αεηιουωάέήίόύώϊϋΐΰ')
    
    while idx < len(word):
        # Digraphs
        if idx + 2 <= len(word) and word[idx:idx+2] in DIGRAPHS_VOWELS:
            units.append({'type': 'V', 'text': word[idx:idx+2], 'sound': DIGRAPHS_VOWELS[word[idx:idx+2]]})
            idx += 2
            continue
        # V+C
        if idx + 2 <= len(word) and word[idx:idx+2] in VC_SEQUENCES:
            # Determine voicing for V+C
            next_char = word[idx+2] if idx + 2 < len(word) else '#'
            is_voiceless = next_char in VOICELESS_CONSONANTS or next_char == '#'
            mapping = VC_SEQUENCES[word[idx:idx+2]]
            sound = mapping['voiceless'] if is_voiceless else mapping['voiced']
            units.append({'type': 'VC', 'text': word[idx:idx+2], 'sound': sound})
            idx += 2
            continue
        # Single Vowel
        if word[idx] in VOWELS:
            sound = VOWELS_SINGLE.get(word[idx], 'V')
            units.append({'type': 'V', 'text': word[idx], 'sound': sound})
            idx += 1
            continue
        # Consonant
        units.append({'type': 'C', 'text': word[idx], 'sound': CONSONANT_MAPPINGS.get(word[idx], word[idx])})
        idx += 1

    # 2. Group into Syllables (Maximal Onset Principle)
    # We iterate backwards? Or forwards with state?
    # Let's try: Nucleus is the anchor.
    # Everything before nucleus (up to prev nucleus) is Onset + Coda of prev.
    # Greek rule: V-CV, V-CCV (if CC is valid onset).
    # For simplicity in this tool: Attach all Cs to the FOLLOWING vowel (Onset) 
    # unless it's a liquid/nasal after a stop? 
    # Let's use a simple "All Cs between Vs go to the next V" rule (CV rule), 
    # except maybe if there are 3 Cs?
    # Actually, for Rhyme Onset detection, we just need to know "What is before the stressed vowel?"
    
    # Let's just reconstruct the phonetic string with markers?
    # Or build a list of (Onset, Nucleus, Coda).
    
    syllables = []
    current_onset = []
    current_nucleus = None
    current_coda = []
    
    # We need to identify nuclei first.
    # Apply Synizesis logic to merge nuclei.
    
    # Pass to merge synizesis
    merged_units = []
    u = 0
    while u < len(units):
        unit = units[u]
        if unit['type'] == 'V':
            # Check synizesis
            is_i = unit['sound'] == 'i'
            is_unstressed = not any(ac in unit['text'] for ac in 'άέήίόύώΐΰ')
            has_next_vowel = (u + 1 < len(units) and units[u+1]['type'] in ('V', 'VC'))
            
            if is_i and is_unstressed and has_next_vowel:
                # It becomes a Glide (Consonant-like)
                unit['type'] = 'G' # Glide
                unit['sound'] = 'j' # Approximate
                merged_units.append(unit)
            else:
                merged_units.append(unit)
        else:
            merged_units.append(unit)
        u += 1
        
    # Now group into syllables
    # Simple algorithm: Split at Vowels.
    # Cs go to the right (Onset) mostly.
    
    # We will build syllables from right to left?
    # Or just collect Cs until V.
    
    current_syllable_chars = []
    syllables_list = []
    
    # This is tricky. Let's do a simple phonetic reconstruction first.
    phonetic_str = ""
    for unit in merged_units:
        # Map sound to ASCII
        s = unit['sound']
        if s in ASCII_PHONETIC: s = ASCII_PHONETIC[s]
        # Handle V+C special mapping (already done in unit['sound']?)
        # VC units have 'av'/'af'.
        phonetic_str += s
        
    # We really just need the "Rhyme Part" for classification.
    # The Rhyme Part is: Stressed Vowel + Everything after.
    # The "Rich Rhyme" check needs: The Onset of the Stressed Syllable.
    
    return [phonetic_str] # TODO: Full syllabification is complex.

def get_rhyme_part_and_onset(w):
    # Normalize
    w_norm = unicodedata.normalize('NFC', w.lower())
    # Find accent index in orthography
    # IMPORTANT: Handle enclisis (two accents, e.g. 'όνομά της').
    # The rhyme stress is the LAST accent.
    accent_idx = -1
    for i, c in enumerate(w_norm):
        if c in 'άέήίόύώΐΰ':
            accent_idx = i
            # Do NOT break. Keep looking for the last one.
    
    # If no accent, assume last vowel (for monosyllables)
    if accent_idx == -1:
        # Find last vowel
        for i in range(len(w_norm)-1, -1, -1):
            if w_norm[i] in 'αεηιουω':
                accent_idx = i
                break
    
    # Now map this to phonetic position.
    # This is hard because of digraphs (2 chars -> 1 sound).
    # We need to tokenize and track indices.
    
    # Reuse tokenization logic
    units = []
    idx = 0
    target_unit_idx = -1
    
    while idx < len(w_norm):
        start_idx = idx
        # Digraphs
        if idx + 2 <= len(w_norm) and w_norm[idx:idx+2] in DIGRAPHS_VOWELS:
            u = {'t': w_norm[idx:idx+2], 's': DIGRAPHS_VOWELS[w_norm[idx:idx+2]], 'is_v': True}
            idx += 2
        elif idx + 2 <= len(w_norm) and w_norm[idx:idx+2] in VC_SEQUENCES:
            # V+C
            mapping = VC_SEQUENCES[w_norm[idx:idx+2]]
            # Check voicing
            next_c = w_norm[idx+2] if idx+2 < len(w_norm) else '#'
            is_vl = next_c in VOICELESS_CONSONANTS or next_c == '#'
            snd = mapping['voiceless'] if is_vl else mapping['voiced']
            u = {'t': w_norm[idx:idx+2], 's': snd, 'is_v': True} # Treat as V unit for indexing
            idx += 2
        elif w_norm[idx] in VOWELS_SINGLE:
            u = {'t': w_norm[idx], 's': VOWELS_SINGLE[w_norm[idx]], 'is_v': True}
            idx += 1
        else:
            # Consonant
            u = {'t': w_norm[idx], 's': CONSONANT_MAPPINGS.get(w_norm[idx], w_norm[idx]), 'is_v': False}
            idx += 1
        
        units.append(u)
        # Check if this unit contains the accent_idx
        if start_idx <= accent_idx < idx:
            target_unit_idx = len(units) - 1
            
    if target_unit_idx == -1:
        return None, None
        
    # Rhyme Part = Unit[target_unit_idx] (Nucleus) + All following units
    # Onset = Units immediately preceding target_unit_idx that are Consonants
    
    rhyme_phonemes = []
    for i in range(target_unit_idx, len(units)):
        s = units[i]['s']
        if s in ASCII_PHONETIC: s = ASCII_PHONETIC[s]
        rhyme_phonemes.append(s)
        
    rhyme_part = "".join(rhyme_phonemes)
    
    onset_phonemes = []
    for i in range(target_unit_idx - 1, -1, -1):
        if not units[i]['is_v']:
            s = units[i]['s']
            if s in ASCII_PHONETIC: s = ASCII_PHONETIC[s]
            onset_phonemes.insert(0, s)
        else:
            break # Stop at previous vowel
    
    onset_part = "".join(onset_phonemes)
    
    return rhyme_part, onset_part

def classify_rhyme_pair(word1: str, word2: str) -> Dict:
    """
    Classify the rhyme between two words.
    Returns:
        {
            'type': 'PURE' | 'RICH' | 'IMPERFECT' | 'NONE',
            'subtype': 'M' | 'F2' | 'F3',
            'details': '...'
        }
    """
    # 1. Get Stress and Phonetics
    # We use the primary stress option
    s1 = detect_stress_position(word1)[0]
    s2 = detect_stress_position(word2)[0]
    
    # If stress types don't match (e.g. M vs F2), it's usually NO rhyme, 
    # unless it's an Imperfect Stress rhyme (rare).
    if s1[1] != s2[1]:
        return {'type': 'NONE', 'reason': 'Stress mismatch'}
    stress_type = s1[1]
    
    # 2. Extract the "Rhyme Part" (Nucleus + Coda of stressed syllable + subsequent syllables)
    rp1, on1 = get_rhyme_part_and_onset(word1)
    rp2, on2 = get_rhyme_part_and_onset(word2)
    
    if not rp1 or not rp2:
        return {'type': 'UNKNOWN'}
        
    # Normalize: remove spaces (e.g. 'mallia su' -> 'malliasu')
    rp1_norm = rp1.replace(' ', '')
    rp2_norm = rp2.replace(' ', '')
        
    # Check Pure Rhyme
    if rp1_norm == rp2_norm:
        # Check Rich Rhyme (Onsets match)
        if on1 and on2 and on1 == on2:
            return {'type': 'RICH', 'subtype': stress_type, 'onset': on1}
        return {'type': 'PURE', 'subtype': stress_type}
        
    # Check Imperfect Rhyme
    # 1. Consonant Mismatch (IMP-C): Stressed Vowel matches, but some following Cs/Vs differ?
    # Actually, usually IMP-C means the Consonants in the rhyme domain differ, but Vowels match.
    # e.g. 'texniti' (iti) vs 'ksafnizi' (izi).
    # Vowels: i, i. Match.
    # Consonants: t vs z. Mismatch.
    
    # 2. Vowel Mismatch (IMP-V): Stressed Vowel differs, but rest matches.
    # e.g. 'xanete' (anete) vs 'jinete' (inete).
    # Stressed V: a vs i. Mismatch.
    # Rest: nete vs nete. Match.
    
    # Helper to extract Vowels and Consonants from Rhyme Part
    def get_cv_pattern(rp):
        # rp is a phonetic string.
        # We need to know which chars are Vowels.
        # ASCII_PHONETIC vowels are: a, e, i, o, u.
        vs = []
        cs = []
        pattern = []
        for char in rp:
            if char in 'aeiou':
                vs.append(char)
                pattern.append('V')
            else:
                cs.append(char)
                pattern.append('C')
        return vs, cs, pattern

    vs1, cs1, pat1 = get_cv_pattern(rp1)
    vs2, cs2, pat2 = get_cv_pattern(rp2)
    
    # Check IMP-V (Stressed Vowel Mismatch, Rest Matches)
    # Usually this means the REST of the string matches perfectly.
    # And the Stressed Vowel is the FIRST vowel in rp1/rp2 (by definition of rhyme part).
    if len(rp1) > 1 and len(rp2) > 1:
        # Check if everything AFTER the first vowel matches
        # This assumes rp starts with the stressed vowel.
        # Does it?
        # get_rhyme_part_and_onset returns "Rhyme Part = Unit[target_unit_idx]...".
        # target_unit_idx is the unit containing the accent.
        # If it's a Vowel Unit, yes.
        # If it's a V+C unit, it starts with V.
        # So yes, rp[0] is likely the vowel (or start of V).
        
        # Let's check if rp1[1:] == rp2[1:] (approximate)
        # Better: Check if vs1[1:] == vs2[1:] AND cs1 == cs2?
        # Example: 'anete' vs 'inete'.
        # vs1: a, e, e. cs1: n, t.
        # vs2: i, e, e. cs2: n, t.
        # vs1[1:] (e,e) == vs2[1:] (e,e).
        # cs1 (n,t) == cs2 (n,t).
        # vs1[0] (a) != vs2[0] (i).
        # This is IMP-V.
        
        if vs1[1:] == vs2[1:] and cs1 == cs2 and vs1[0] != vs2[0]:
             # STRICTNESS CHECK:
             # If there are NO consonants, and vowels differ, is it a rhyme?
             # e.g. 'o' vs 'i' (open syllables).
             # cs1=[], cs2=[]. vs1=['o'], vs2=['i'].
             # vs1[1:]=[], vs2[1:]=[]. Match.
             # This passes the check.
             # But 'o' vs 'i' is NOT a rhyme.
             # We require at least ONE consonant to match for IMP-V, OR at least one vowel after the stressed one.
             # i.e. len(rp) > 1 is not enough if rp is just V.
             
             if not cs1 and not vs1[1:]:
                 # Single vowel mismatch. Reject.
                 return {'type': 'NONE', 'reason': 'Single vowel mismatch (IMP-V rejected)'}
                 
             # Also reject if just V+V mismatch? e.g. 'ae' vs 'oe'?
             # vs1=['a','e'], vs2=['o','e']. cs1=[], cs2=[].
             # vs1[1:]=['e'] == vs2[1:]=['e']. Match.
             # 'ae' vs 'oe'. Assonance? Maybe.
             # But 'o' vs 'i' (single V) is definitely bad.
             
             return {'type': 'IMPERFECT', 'subtype': stress_type, 'imperfect_type': 'IMP-V', 'details': f"{vs1[0]}-{vs2[0]}"}
             # If there are NO consonants (cs1 is empty), then we just have Vowel mismatch.
             # e.g. 'o' vs 'i' (Oxytones). This is NOT a rhyme.
             # e.g. 'aa' vs 'ia' (Paroxytones with hiatus?). 'a' vs 'a' match.
             # But if cs1 is empty, we need to be careful.
             # If len(vs1) == 1 (just the stressed vowel), and it differs -> NO RHYME.
             if len(vs1) == 1 and not cs1:
                 return {'type': 'NONE', 'reason': 'Vowel mismatch in open syllable'}
                 
             return {'type': 'IMPERFECT', 'subtype': 'IMP-V', 'details': f"{vs1[0]}-{vs2[0]}"}

    # Check IMP-C (Vowels Match, Consonants Differ)
    # Check IMP-C (Vowels Match, Consonants Differ)
    if vs1 == vs2:
        # Vowels match perfectly.
        # Consonants must differ.
        if cs1 != cs2:
            # STRICTNESS CHECK:
            # "tis" (is) vs "puli" (uli) -> vs=['i'], ['u','i']? No, rhyme part of puli is 'uli' (F2) or 'i' (M)?
            # If stress matches (M), then 'tis' -> 'is'. 'puli' -> 'i'.
            # vs1=['i'], vs2=['i']. Match.
            # cs1=['s'], cs2=[]. Mismatch.
            # This is Assonance (IMP-C).
            # BUT "tis" vs "puli" is weird.
            # Usually we want at least SOME consonant overlap or similar structure.
            # If one is Open (ends in V) and other is Closed (ends in C), it's a weak rhyme.
            # For strict corpus, let's REJECT if one is Open and other is Closed.
            
            # Check if they end in Vowel or Consonant
            # rp1/rp2 are phonetic strings.
            # Vowels: a,e,i,o,u
            # is_open1 = rp1[-1] in 'aeiou'
            # is_open2 = rp2[-1] in 'aeiou'
            
            # if is_open1 != is_open2:
            #    return {'type': 'NONE', 'reason': 'Open/Closed mismatch'}
            # REMOVED to allow IMP-0 (Consonant vs Zero) as per Topintzi et al.
            
            # STRICT CONSONANT COMPATIBILITY CHECK
            # We only allow IMP-C if the consonants are phonetically similar.
            # Updated based on Topintzi et al. (2019):
            # Allow Place-sharing pairs (e.g. z/t) even if voicing/manner differs.
            
            def is_subsequence(sub, main):
                """Check if sub is a subsequence of main"""
                it = iter(main)
                return all(c in it for c in sub)

            def are_consonants_compatible(c_list1, c_list2):
                # IMP-0 Check: Subsequence of consonants (Deletion/Insertion)
                # Topintzi et al: IMP-0 is Consonant vs Zero.
                # e.g. 'st' vs 't' (s deleted). 't' is subsequence of 'st'.
                # e.g. 'st' vs 's' (t deleted). 's' is subsequence of 'st'.
                # e.g. 'mps' vs 'n'. 'n' is NOT subsequence.
                
                # CRITICAL FIX: Reject open vs closed syllable mismatch
                # Empty list is technically a subsequence of anything, but that's a false positive!
                # e.g. "τυχερό" (no consonant) vs "δαρτός" (s) should NOT rhyme
                if not c_list1 or not c_list2:
                    # One is open syllable, other is closed. Reject.
                    return False
                
                if len(c_list1) != len(c_list2):
                     # Check subsequence
                     if len(c_list1) < len(c_list2):
                         if is_subsequence(c_list1, c_list2): return "IMP-0"
                     else:
                         if is_subsequence(c_list2, c_list1): return "IMP-0"
                     
                     # If lengths differ and NOT subsequence, REJECT.
                     # "kleftis" (f,t,s) vs "meni" (n). Rejected.
                     # "lampsi" (m,p,s) vs "fthani" (n). Rejected.
                     return False
                
                # Lengths match. Check compatibility (IMP-C).
                for c1, c2 in zip(c_list1, c_list2):
                    if c1 == c2: continue
                    
                    f1 = CONSONANT_FEATURES.get(c1)
                    f2 = CONSONANT_FEATURES.get(c2)
                    
                    if not f1 or not f2:
                        return False # Unknown char
                        
                    # Calculate distance
                    # Place mismatch?
                    place_match = f1[0] == f2[0]
                    manner_match = f1[1] == f2[1]
                    
                    # Allow if Place matches (e.g. z/t, s/T)
                    if place_match:
                        continue
                        
                    # Allow if Manner matches (e.g. m/n - Nasals)
                    if manner_match:
                        continue
                        
                    # Reject if Place AND Manner differ.
                    is_obstruent1 = f1[1] <= 2
                    is_obstruent2 = f2[1] <= 2
                    
                    if is_obstruent1 != is_obstruent2:
                        return False # Reject Obstruent vs Sonorant
                        
                    continue
                    
                return "IMP-C"

            compatibility = are_consonants_compatible(cs1, cs2)
            
            if compatibility == "IMP-0":
                 return {'type': 'IMPERFECT', 'subtype': stress_type, 'imperfect_type': 'IMP-0', 'details': f"{cs1}-{cs2}"}
            elif compatibility == "IMP-C":
                 return {'type': 'IMPERFECT', 'subtype': stress_type, 'imperfect_type': 'IMP-C', 'details': f"{cs1}-{cs2}"}
            else:
                 return {'type': 'NONE', 'reason': 'Incompatible consonants for IMP-C'}

    # Check IMP-0 (Consonant vs Zero) - handled above now?
    # The block below (lines 850+) checked for prefix/suffix match.
    # My new logic handles subsequence, which is strictly better than prefix/suffix.
    # So I can remove the old IMP-0 block or merge it.
    # But wait, the old block checked `rp1.startswith(rp2)`.
    # That is a subset of subsequence.
    # So the new logic covers it.
    # I should remove the old block to avoid duplicate/conflicting logic.
    
    return {'type': 'NONE', 'subtype': stress_type, 'r1': rp1, 'r2': rp2}

    # Check Combined Imperfect (IMP-V + IMP-0)
    # e.g. 'is' vs 'a' (i vs a AND s vs 0)
    # This is very loose.
    # Maybe just check if they are both short?
    
    return {'type': 'NONE', 'subtype': stress_type, 'r1': rp1, 'r2': rp2}

def analyze_mosaic_pattern(line1: str, line2: str) -> Dict:
    """
    Specialized analysis for MOSAIC rhyme detection
    
    Returns detailed breakdown of word boundaries and phonetic alignment
    """
    r1 = extract_rhyme_domain(line1, include_context=True)
    r2 = extract_rhyme_domain(line2, include_context=True)
    
    analysis = {
        'line1': line1,
        'line2': line2,
        'line1_rhyme': r1,
        'line2_rhyme': r2,
        'stress_match': r1['stress_type'] == r2['stress_type'],
        'both_multi_word': r1['is_potential_mosaic'] and r2['is_potential_mosaic']
    }
    
    # Check if phonetic rhyme spans word boundary
    if r1['is_potential_mosaic'] or r2['is_potential_mosaic']:
        # STRICT CHECK: Do the phonetics actually match?
        # We need to compare the RHYME PART (from stressed vowel onwards).
        # r1['rhyme_domain'] is the text.
        rp1, _ = get_rhyme_part_and_onset(r1['rhyme_domain'])
        rp2, _ = get_rhyme_part_and_onset(r2['rhyme_domain'])
        
        if rp1 and rp2 and rp1.replace(' ', '') == rp2.replace(' ', ''):
            analysis['mosaic_candidate'] = True
            analysis['explanation'] = f"MOSAIC MATCH: {rp1} == {rp2}"
        else:
            analysis['mosaic_candidate'] = False
            analysis['explanation'] = f"MOSAIC MISMATCH: {rp1} != {rp2}"
    else:
        analysis['mosaic_candidate'] = False
    
    return analysis

def format_for_llm_prompt(analysis: Dict) -> str:
    """
    Format phonetic analysis in LLM-friendly way (NO IPA!)
    
    Uses simplified ASCII notation:
    - Stressed vowel in CAPS: ka-LA, ka-LI
    - Word boundaries marked: "| |"
    - Simple consonants: T=θ, D=ð, G=γ, X=χ
    """
    r1 = analysis['line1_rhyme']
    r2 = analysis['line2_rhyme']
    
    formatted = f"""
PHONETIC ANALYSIS (Stress: {r1['stress_type']} / {r2['stress_type']}):

Line 1 final: "{' | '.join(r1['words'])}"
  → Sound: {r1['rhyme_domain_phonetic']}

Line 2 final: "{' | '.join(r2['words'])}"
  → Sound: {r2['rhyme_domain_phonetic']}

MOSAIC CHECK: {"YES - rhyme spans words" if analysis['mosaic_candidate'] else "NO - single word rhyme"}
"""
    
    return formatted

def extract_pre_rhyme_vowel(w: str) -> str:
    """
    Extracts the vowel of the syllable immediately preceding the stressed syllable.
    Used for IDV (Pre-rhyme Identical Vowel) detection.
    """
    w_norm = unicodedata.normalize('NFC', w.lower())
    # Find accent index
    accent_idx = -1
    for i, c in enumerate(w_norm):
        if c in 'άέήίόύώΐΰ':
            accent_idx = i
            # Keep looking for last accent (enclisis)
    
    if accent_idx == -1:
        # Try last vowel fallback
        for i in range(len(w_norm)-1, -1, -1):
            if w_norm[i] in 'αεηιουω':
                accent_idx = i
                break
    
    if accent_idx <= 0: return ""
    
    # Get substring before accent
    pre_chunk = w_norm[:accent_idx]
    if not pre_chunk: return ""
    
    # Phoneticize
    phon = g2p_greek(pre_chunk)
    
    # Find last vowel in phon
    # ASCII_PHONETIC vowels: a, e, i, o, u
    for char in reversed(phon):
        if char in 'aeiou':
            return char
            
    return ""
