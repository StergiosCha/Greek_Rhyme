"""
RAG System for Greek Rhyme Examples
Retrieves relevant examples from Greek Rhyme corpus
"""
import json
from typing import List, Dict
import re

# Sample rhyme corpus (in production, this would be loaded from database/vector store)
import os
from pathlib import Path

# Load rhyme corpus from JSON
# Using the definitive corpus from the dataset repository
# Using Enhanced Regular for strict rhyme classification with full context
CORPUS_PATH = Path(__file__).parent.parent / "data" / "complete_corpus_enhanced.json"

try:
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    
    # Check if it's Enhanced format (single object with "entries" array)
    if "entries" in loaded_data and isinstance(loaded_data["entries"], list):
        print(f"Loaded Enhanced corpus format with {len(loaded_data['entries'])} total entries")
        # Reorganize by poet for easier retrieval
        RHYME_CORPUS = {}
        for entry in loaded_data["entries"]:
            poet = entry.get("poet", "Unknown")
            if poet not in RHYME_CORPUS:
                RHYME_CORPUS[poet] = {
                    "poet": poet,
                    "entries": []
                }
            RHYME_CORPUS[poet]["entries"].append(entry)
        print(f"Reorganized into {len(RHYME_CORPUS)} poets")
    else:
        # Regular format (dict of poets)
        RHYME_CORPUS = loaded_data
        print(f"Loaded RAG corpus from {CORPUS_PATH.name} with {len(RHYME_CORPUS)} poets.")
except FileNotFoundError:
    print(f"Warning: {CORPUS_PATH} not found. Using empty corpus.")
    RHYME_CORPUS = {}

def extract_rhyme_features(text: str) -> List[str]:
    """Extract potential rhyme features from text"""
    features = []
    
    # Check for position mentions
    if any(word in text.lower() for word in ['τελικ', 'τελευταί', 'final']):
        features.append('M')
    if any(word in text.lower() for word in ['παραλήγουσ', 'penult']):
        features.append('F2')
    if any(word in text.lower() for word in ['προπαραλήγουσ', 'antepenult']):
        features.append('F3')
    
    # Check for feature mentions
    if any(word in text.lower() for word in ['πλούσι', 'rich', 'onset']):
        features.append('RICH')
    if any(word in text.lower() for word in ['ατελ', 'imperfect', 'μερικ']):
        features.append('IMP')
    if any(word in text.lower() for word in ['μωσαϊκ', 'mosaic', 'λέξ']):
        features.append('MOS')
    if any(word in text.lower() for word in ['αντιγραφ', 'copy', 'επανάληψ']):
        features.append('COPY')
    
    return features

async def get_relevant_examples(query_text: str, top_k: int = 5) -> str:
    """
    Retrieve relevant rhyme examples for identification task
    Simple keyword-based retrieval (in production, use embeddings)
    """
    query_features = extract_rhyme_features(query_text)
    
    relevant_examples = []
    
    # Simple scoring: match features and poet mentions
    for corpus_key, corpus_data in RHYME_CORPUS.items():
        # Skip non-dict entries (metadata keys)
        if not isinstance(corpus_data, dict):
            continue
            
        score = 0
        
        # Handle different structure keys (examples vs entries)
        examples = corpus_data.get("examples", corpus_data.get("entries", []))
        
        # Check if poet mentioned in query
        poet_name = corpus_data.get("poet", corpus_key)
        if poet_name in query_text:
            score += 10
        
        # Check examples for feature matches
        for example in examples:
            matched_features = len(set(query_features) & set(example["features"]))
            if matched_features > 0:
                score += matched_features * 2
                relevant_examples.append({
                    "example": example,
                    "poet": poet_name,
                    "poem": corpus_data.get("poem", "Unknown"),
                    "score": score
                })
    
    # Sort by score and take top_k
    relevant_examples.sort(key=lambda x: x["score"], reverse=True)
    top_examples = relevant_examples[:top_k]
    
    if not top_examples:
        # Return generic examples
        return format_generic_examples()
    
    # Format examples
    formatted = "RELEVANT EXAMPLES FROM CORPUS:\n\n"
    for i, item in enumerate(top_examples, 1):
        ex = item["example"]
        
        # Handle different example structures (lines vs rhyme_pair)
        lines = ex.get("lines", ex.get("rhyme_pair", []))
        line_nums = ex.get("line_numbers", ex.get("line_indices", []))
        phonetic = ex.get("phonetic", [])
        
        formatted += f"Example {i} ({item['poet']}):\n"
        formatted += f"Lines {line_nums}: {lines}\n"
        formatted += f"Classification: {ex['classification']}\n"
        formatted += f"Phonetic: {phonetic}\n"
        formatted += f"Features: {', '.join(ex['features'])}\n\n"
    
    return formatted

async def get_generation_examples(rhyme_type: str, features: List[str], 
                                 theme: str, poet: str = None, top_k: int = 15) -> str:
    """
    Retrieve examples for generation task based on desired rhyme pattern
    If poet is specified, filter by that poet's style
    """
    relevant_examples = []
    
    # Filter corpus by poet if specified
    corpus_to_search = RHYME_CORPUS
    if poet:
        # Find matching poet in corpus
        corpus_to_search = {k: v for k, v in RHYME_CORPUS.items() if v.get("poet", k) == poet}
        if not corpus_to_search:
            print(f"Warning: Poet '{poet}' not found in corpus, using all poets")
            corpus_to_search = RHYME_CORPUS
            
    # Iterate through corpus to find matches
    # Shuffle poets to get diversity
    import random
    poet_keys = list(corpus_to_search.keys())
    random.shuffle(poet_keys)
    
    for corpus_key in poet_keys:
        corpus_data = corpus_to_search[corpus_key]
        
        # Skip metadata
        if not isinstance(corpus_data, dict):
            continue
            
        # Handle different structure keys (examples vs entries)
        examples = corpus_data.get("examples", corpus_data.get("entries", []))
        
        # Limit examples per poet to ensure diversity (unless specific poet requested)
        poet_examples_count = 0
        max_per_poet = 3 if not poet else top_k
        
        # Shuffle examples within poet too
        examples_copy = examples.copy()
        random.shuffle(examples_copy)
        
        for example in examples_copy:
            if poet_examples_count >= max_per_poet:
                break
            # Validate first!
            lines = example.get("lines", example.get("rhyme_pair", []))
            if not lines or len(lines) < 2: continue
            
            w1 = lines[0].split()[-1].strip('.,;!?')
            w2 = lines[1].split()[-1].strip('.,;!?')
            
            # Filter out identical word rhymes (COPY)
            if w1.lower() == w2.lower():
                continue
                
            # Filter out "cheap" rhymes where one word is contained in the other
            # e.g. "φούμαρα" / "εφούμαρα"
            # This helps avoid cognate rhymes which confuse the model about RICH rhyming
            if len(w1) > 3 and len(w2) > 3:
                if w1.lower().endswith(w2.lower()) or w2.lower().endswith(w1.lower()):
                    continue
            
            # Quick validation
            # If "MOS" in features, assume valid (since we fixed validation logic but it's expensive to run full mosaic check here?)
            # Actually, let's just trust the "valid" ones or run a quick check.
            # For performance, we might want to pre-validate.
            # But for this prototype, let's run classify_rhyme_pair if it's not MOS.
            
            is_valid_candidate = True
            if "MOS" not in example["features"]:
                from greek_phonology import classify_rhyme_pair
                res = classify_rhyme_pair(w1, w2)
                if res['type'] == 'NONE':
                    is_valid_candidate = False
            
            if not is_valid_candidate:
                continue

            score = 0
            
            # STRICT RHYME TYPE MATCHING
            # If user asks for F3, we generally don't want F2 or M.
            # However, sometimes M/F1 are ambiguous.
            # But for strict generation, let's enforce it.
            if rhyme_type and rhyme_type not in example["features"]:
                # Special case: M and F1 might be interchangeable in some contexts,
                # but usually the corpus uses one consistent label.
                # If requested 'M', and corpus has 'F1', maybe allow?
                # For now, let's be strict.
                continue
            
            # Score boost for rhyme type (redundant if strict, but keeps logic consistent)
            score += 5

            # STRICT FEATURE MATCHING
            # If user asks for IDV, RICH, or MOSAIC, the example MUST have it.
            missing_required_feature = False
            for req_feature in features:
                # Handle aliases and checking
                check_feature = req_feature
                
                # Special handling for MOSAIC/MOS
                if check_feature in ["MOS", "MOSAIC"]:
                    has_it = "MOS" in example["features"] or "MOSAIC" in example["features"]
                elif check_feature == "IDV" or check_feature == "COPY":
                    has_it = check_feature in example["features"]
                elif check_feature == "RICH":
                    # RICH means ONLY RICH, exclude PURE and IMPERFECT
                    has_rich = "RICH" in example["features"]
                    has_pure = "PURE" in example["features"]
                    has_imp = "IMP" in example["features"] or "IMPERFECT" in example["features"]
                    has_it = has_rich and not has_pure and not has_imp
                elif check_feature in ["IMPERFECT", "IMP"]:
                    # IMPERFECT means ONLY IMPERFECT, exclude PURE and RICH
                    has_imp = "IMP" in example["features"] or "IMPERFECT" in example["features"]
                    has_pure = "PURE" in example["features"]
                    has_rich = "RICH" in example["features"]
                    has_it = has_imp and not has_pure and not has_rich
                elif check_feature == "pure":
                    # PURE means NO RICH and NO IMPERFECT
                    # Check that example doesn't have RICH or IMP tags
                    has_rich = "RICH" in example["features"]
                    has_imp = "IMP" in example["features"] or "IMPERFECT" in example["features"]
                    has_it = not (has_rich or has_imp)
                else:
                    # Ignore other features (metadata)
                    continue
                    
                if not has_it:
                    missing_required_feature = True
                    break

                    
                    # EXTRA VERIFICATION FOR IDV
                    # The corpus sometimes mislabels IDV (e.g. 'γεμίζει' / 'χείλη').
                    # We must verify it phonetically.
                    if check_feature == "IDV":
                        # Simple heuristic to check pre-stress vowel
                        # We need to find the vowel before the stressed syllable.
                        # Since we don't have full G2P here easily without overhead,
                        # let's use a simple orthographic check on the words.
                        
                        # Helper to find pre-stress vowel
                        def get_pre_stress_vowel_simple(word):
                            accent_chars = 'άέήίόύώ'
                            vowels = 'αεηιουωάέήίόύώ'
                            stress_idx = -1
                            for i, c in enumerate(word):
                                if c in accent_chars:
                                    stress_idx = i
                                    break
                            
                            if stress_idx <= 0: return None # No stress or stress at start
                            
                            start_scan = stress_idx - 1
                            
                            # Handle Digraphs at stress (e.g. 'ού', 'εί', 'αί', 'οί')
                            # If the accented char is the second part of a digraph, the first part is NOT the pre-stress vowel.
                            # e.g. 'σταματούν' (stress on ύ). 'ο' is part of 'ου'.
                            if start_scan >= 0:
                                prev = word[start_scan].lower()
                                curr = word[stress_idx].lower()
                                # Check pairs: ου, ει, αι, οι, υι
                                # Note: curr has accent. prev does not.
                                # 'ού' -> prev='ο', curr='ύ'
                                # 'εί' -> prev='ε', curr='ί'
                                # 'αί' -> prev='α', curr='ί'
                                # 'οί' -> prev='ο', curr='ί'
                                # 'υί' -> prev='υ', curr='ί'
                                is_digraph = False
                                if prev == 'ο' and curr in ['ύ', 'ί']: is_digraph = True # ου, οι
                                elif prev == 'ε' and curr == 'ί': is_digraph = True # ει
                                elif prev == 'α' and curr == 'ί': is_digraph = True # αι
                                elif prev == 'υ' and curr == 'ί': is_digraph = True # υι
                                
                                if is_digraph:
                                    start_scan -= 1

                            # Scan backwards
                            for i in range(start_scan, -1, -1):
                                char = word[i].lower()
                                # Synizesis handling:
                                # If we find 'ι' immediately before the stressed vowel (or digraph), treat it as a glide
                                # But we need to be careful. If we skipped a digraph char, we are now at stress_idx - 2.
                                # If word is 'παιδιά' [pe-dja]. Stress 'ά'. Digraph? No.
                                # 'καπνιά' [ka-pnja]. Stress 'ά'. 'ι' is at -1.
                                # 'ποιοί' [pji]. Stress 'ί'. Digraph 'οί'. Skipped 'ο'. Now at 'ι'.
                                # 'ι' is glide [j]. So skip 'ι' too? Yes.
                                
                                # Simple rule: if we see 'ι' immediately at current scan pos, 
                                # AND it's adjacent to the stress complex, skip it.
                                # (This assumes 'ι' is glide).
                                if i == start_scan and char == 'ι':
                                    continue
                                    
                                if char in vowels:
                                    return char
                            return None

                        # Map vowels to phonetic sounds
                        phonetic_map = {
                            'α': 'a', 'ά': 'a',
                            'ε': 'e', 'έ': 'e', 'αι': 'e',
                            'η': 'i', 'ή': 'i', 'ι': 'i', 'ί': 'i', 'υ': 'i', 'ύ': 'i', 'ει': 'i', 'οι': 'i',
                            'ο': 'o', 'ό': 'o', 'ω': 'o', 'ώ': 'o',
                            'ου': 'u'
                        }
                        
                        v1 = get_pre_stress_vowel_simple(w1)
                        v2 = get_pre_stress_vowel_simple(w2)
                        
                        if not v1 or not v2:
                            missing_required_feature = True # One word starts with stress -> No IDV
                        else:
                            p1 = phonetic_map.get(v1, v1)
                            p2 = phonetic_map.get(v2, v2)
                            if p1 != p2:
                                missing_required_feature = True
                        
                        if missing_required_feature:
                            break

            if missing_required_feature:
                continue

            # Match additional features (score boost)
            matched_features = len(set(features) & set(example["features"]))
            score += matched_features * 3

            # Boost for Non-Trivial Mosaics
            # Check for both 'MOS' and 'MOSAIC' since corpus might use either
            is_mosaic_requested = "MOS" in features or "MOSAIC" in features
            is_mosaic_example = "MOS" in example["features"] or "MOSAIC" in example["features"]
            
            if is_mosaic_requested and is_mosaic_example:
                # Check if it's a "trivial" mosaic (clitic based)
                common_clitics = {'μου', 'σου', 'του', 'της', 'μας', 'σας', 'τους', 'τον', 'την', 'το', 'τα', 'των',
                                  'mu', 'su', 'tu', 'tis', 'mas', 'sas', 'tus', 'ton', 'tin', 'to', 'ta'}
                
                # Handle both 'lines' and 'rhyme_pair' keys
                lines_to_check = example.get("lines", example.get("rhyme_pair", []))
                is_trivial = True
                if len(lines_to_check) >= 2:
                    # Robust cleaning using regex to remove all non-alphanumeric chars
                    w1_raw = lines_to_check[0].split()[-1].lower()
                    w2_raw = lines_to_check[1].split()[-1].lower()
                    
                    # Keep only greek/latin letters
                    w1 = re.sub(r'[^\w]', '', w1_raw)
                    w2 = re.sub(r'[^\w]', '', w2_raw)
                    
                    # If BOTH are clitics, it's very trivial.
                    # If ONE is not a clitic, it's interesting!
                    if w1 not in common_clitics or w2 not in common_clitics:
                        is_trivial = False
                
                if not is_trivial:
                    score += 15  # Huge boost for interesting mosaics
                    # print(f"DEBUG: Boosted {w1}/{w2} (+15)")
                else:
                    score -= 2   # Slight penalty for trivial ones to prefer variety if available
                    # print(f"DEBUG: Penalized {w1}/{w2} (-2)")
            
            # Boost score if poet-specific and we found matches
            poet_name = corpus_data.get("poet", corpus_key)
            if poet and poet_name == poet:
                score += 10
            
            if score > 0:
                # print(f"DEBUG: Candidate {poet_name} {lines} Score: {score}")
                relevant_examples.append({
                    "example": example,
                    "poet": poet_name,
                    "poem": corpus_data.get("poem", "Unknown"),
                    "score": score
                })
                poet_examples_count += 1
    
    relevant_examples.sort(key=lambda x: x["score"], reverse=True)
    top_examples = relevant_examples[:top_k]
    
    if not top_examples:
        # DO NOT FALLBACK TO GENERIC EXAMPLES
        # If strict filtering is on, we want to know if nothing was found.
        return "" 
        # return format_generic_generation_examples(rhyme_type, features)
    
    # Format with poet style info if specified
    poet_info = f" in the style of {poet}" if poet else ""
    formatted = f"VERIFIED EXAMPLES WITH {rhyme_type} RHYME AND FEATURES {', '.join(features)}{poet_info}:\n\n"
    for i, item in enumerate(top_examples, 1):
        ex = item["example"]
        lines = ex.get("lines", ex.get("rhyme_pair", []))
        formatted += f"Example {i} from {item['poet']}:\n"
        formatted += f"Lines: {' / '.join(lines)}\n"
        formatted += f"Pattern: {ex['classification']}\n"
        phonetic = ex.get('phonetic', ['N/A', 'N/A'])
        formatted += f"Phonetic structure: {' / '.join(phonetic)}\n\n"
    
    # Add relevant statistics
    formatted += "\nRELEVANT CORPUS STATISTICS:\n"
    for corpus_key, corpus_data in corpus_to_search.items():
        if not isinstance(corpus_data, dict):
            continue
        poet_name = corpus_data.get("poet", corpus_key)
        if any(e["poet"] == poet_name for e in top_examples):
            poem_name = corpus_data.get("poem", "Various works")
            formatted += f"\n{poet_name} ({poem_name}):\n"
            stats = corpus_data.get("stats", {})
            if stats:
                for stat_key, stat_val in stats.items():
                    if rhyme_type.lower() in stat_key.lower() or any(f.lower() in stat_key.lower() for f in features):
                        formatted += f"  - {stat_key}: {stat_val}%\n"
            else:
                formatted += f"  - Total examples: {len(corpus_data.get('entries', corpus_data.get('examples', [])))}\n"
    
    return formatted

def format_generic_examples() -> str:
    """Return generic examples when no specific match found"""
    return """GENERAL RHYME EXAMPLES:

1. M-IDV (Masculine with pre-vowel identity):
   "ξανθή" [ksan-'Ti] / "γραφή" [Gra-'fi]
   Final stress, vowel 'i' matches, pre-vowel 'A' matches

2. F2-MOS (Feminine-2 Mosaic):
   "όνομά της" ['no-ma tis] / "ο μπάτης" [o 'ba-tis]
   Penultimate stress, crosses word boundaries

3. F3-IMP-V (Feminine-3 Imperfect Vowel):
   "στόματα" ['sto-ma-ta] / "σώματα" ['so-ma-ta]
   Antepenultimate stress, vowel variation
"""

def format_generic_generation_examples(rhyme_type: str, features: List[str]) -> str:
    """Return generic generation examples"""
    examples = {
        "M": "Examples with Masculine rhyme:\n- καρδιά / αγαπημένη μου φωτιά\n- νερό / χειμωνιάτικο πρωινό",
        "F2": "Examples with Feminine-2 rhyme:\n- τραγούδι / ανοιξιάτικο λουλούδι\n- μάτια / χρυσά παιδικά χάδια",
        "F3": "Examples with Feminine-3 rhyme:\n- άνθρωπος / μοναχικός τόπος\n- θάλασσα / γαλάζια απέραντη μάζα"
    }
    
    base = examples.get(rhyme_type, "")
    
    if "RICH" in features:
        base += "\n\nFor RICH rhymes, match onset consonants:\n- καλά / ξαλά (onset 'k' vs 'ks')\n- μόνη / αγαπημένη ('m' vs 'm')"
    
    if "IDV" in features:
        base += "\n\nFor IDV, match pre-stress vowel:\n- ανάσα / χαρά σας (pre-vowel 'a')"
    
    return base

    return stats

def validate_corpus():
    """
    Validate the rhyme corpus using the phonology module.
    Returns a report of valid/invalid examples.
    """
    from greek_phonology import classify_rhyme_pair
    
    report = {
        "valid": 0,
        "invalid": 0,
        "details": []
    }
    
    for corpus_key, corpus_data in RHYME_CORPUS.items():
        # Skip non-dict entries (metadata keys)
        if not isinstance(corpus_data, dict):
            continue
            
        # Handle different structure keys
        examples = corpus_data.get("examples", corpus_data.get("entries", []))
        
        for example in examples:
            lines = example.get("lines", example.get("rhyme_pair", []))
            if not lines or len(lines) < 2: continue
            # Extract last word of each line
            w1 = lines[0].split()[-1].strip('.,;!?')
            w2 = lines[1].split()[-1].strip('.,;!?')
            
            # Check for Mosaic
            if "MOS" in example["features"]:
                from greek_phonology import analyze_mosaic_pattern
                # Use full lines
                res_mosaic = analyze_mosaic_pattern(lines[0], lines[1])
                if res_mosaic['mosaic_candidate']:
                    # It is a valid mosaic rhyme candidate
                    res = {'type': 'MOSAIC', 'subtype': 'F2'} # Simplified
                else:
                    # Fallback to standard classification to see what's wrong
                    res = classify_rhyme_pair(w1, w2)
            else:
                # Classify standard
                res = classify_rhyme_pair(w1, w2)
            
            # Check if classification matches claimed features
            claimed_type = "PURE"
            if "RICH" in example["features"]: claimed_type = "RICH"
            if "IMP" in example["features"] or "IMP-V" in example["features"] or "IMP-C" in example["features"]: claimed_type = "IMPERFECT"
            
            # Allow PURE to match RICH (since Rich is a subset of Pure in some views, or vice versa)
            # My classifier returns RICH if onsets match.
            # If corpus says PURE but classifier says RICH -> Acceptable (it is a rhyme).
            # If corpus says RICH but classifier says PURE -> Warning (not rich?).
            # If corpus says IMPERFECT but classifier says PURE -> Warning.
            # If classifier says NONE -> INVALID.
            
            is_valid = True
            msg = ""
            
            if res['type'] == 'NONE':
                is_valid = False
                msg = f"Phonology found NO rhyme for {w1}-{w2}"
            elif res['type'] != claimed_type:
                # Relaxed check
                if claimed_type == 'PURE' and res['type'] == 'RICH':
                    pass # OK
                elif claimed_type == 'IMPERFECT' and res['type'] in ('PURE', 'RICH'):
                    msg = f"Claimed IMPERFECT but found {res['type']}"
                    # Maybe acceptable if we are strict?
                elif res['type'] == 'IMPERFECT' and claimed_type == 'PURE':
                     msg = f"Claimed PURE but found IMPERFECT ({res['subtype']})"
                     is_valid = False
                elif claimed_type == 'RICH' and res['type'] == 'PURE':
                     msg = f"Claimed RICH but found PURE (Onsets didn't match?)"
                     # is_valid = False # Strict?
            
            if is_valid:
                report["valid"] += 1
                # Update example with verified phonetic data?
                # example['phonetic_verified'] = res
            else:
                report["invalid"] += 1
                report["details"].append({
                    "poet": corpus_data.get("poet", corpus_key),
                    "words": f"{w1}-{w2}",
                    "claimed": example["classification"],
                    "found": res,
                    "msg": msg
                })
                
    return report
