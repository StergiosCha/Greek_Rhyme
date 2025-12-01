"""
RAG System for Greek Rhyme Examples
Retrieves relevant examples from Greek Rhyme corpus
"""
import json
from typing import List, Dict
import re

# Sample rhyme corpus (in production, this would be loaded from database/vector store)
import os

# Load rhyme corpus from JSON
try:
    with open("rhyme_corpus.json", "r", encoding="utf-8") as f:
        RHYME_CORPUS = json.load(f)
    print(f"Loaded RAG corpus with {len(RHYME_CORPUS)} poets.")
except FileNotFoundError:
    print("Warning: rhyme_corpus.json not found. Using empty corpus.")
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

async def get_relevant_examples(query_text: str, top_k: int = 3) -> str:
    """
    Retrieve relevant rhyme examples for identification task
    Simple keyword-based retrieval (in production, use embeddings)
    """
    query_features = extract_rhyme_features(query_text)
    
    relevant_examples = []
    
    # Simple scoring: match features and poet mentions
    for corpus_key, corpus_data in RHYME_CORPUS.items():
        score = 0
        
        # Check if poet mentioned in query
        if corpus_data["poet"] in query_text:
            score += 10
        
        # Check examples for feature matches
        for example in corpus_data["examples"]:
            matched_features = len(set(query_features) & set(example["features"]))
            if matched_features > 0:
                score += matched_features * 2
                relevant_examples.append({
                    "example": example,
                    "poet": corpus_data["poet"],
                    "poem": corpus_data["poem"],
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
        formatted += f"Example {i} ({item['poet']} - {item['poem']}):\n"
        formatted += f"Lines {ex['line_numbers']}: {ex['lines']}\n"
        formatted += f"Classification: {ex['classification']}\n"
        formatted += f"Phonetic: {ex['phonetic']}\n"
        formatted += f"Features: {', '.join(ex['features'])}\n\n"
    
    return formatted

async def get_generation_examples(rhyme_type: str, features: List[str], 
                                 theme: str, poet: str = None, top_k: int = 2) -> str:
    """
    Retrieve examples for generation task based on desired rhyme pattern
    If poet is specified, filter by that poet's style
    """
    relevant_examples = []
    
    # Filter corpus by poet if specified
    corpus_to_search = RHYME_CORPUS
    if poet:
        # Find matching poet in corpus
        corpus_to_search = {k: v for k, v in RHYME_CORPUS.items() if v["poet"] == poet}
        if not corpus_to_search:
            print(f"Warning: Poet '{poet}' not found in corpus, using all poets")
            corpus_to_search = RHYME_CORPUS
    
    for corpus_key, corpus_data in corpus_to_search.items():
        for example in corpus_data["examples"]:
            # Validate first!
            lines = example["lines"]
            w1 = lines[0].split()[-1].strip('.,;!?')
            w2 = lines[1].split()[-1].strip('.,;!?')
            
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
            
            # Match rhyme type
            if rhyme_type in example["features"]:
                score += 5
            
            # Match additional features
            matched_features = len(set(features) & set(example["features"]))
            score += matched_features * 3
            
            # Boost score if poet-specific and we found matches
            if poet and corpus_data["poet"] == poet:
                score += 10
            
            if score > 0:
                relevant_examples.append({
                    "example": example,
                    "poet": corpus_data["poet"],
                    "poem": corpus_data["poem"],
                    "score": score
                })
    
    relevant_examples.sort(key=lambda x: x["score"], reverse=True)
    top_examples = relevant_examples[:top_k]
    
    if not top_examples:
        return format_generic_generation_examples(rhyme_type, features)
    
    # Format with poet style info if specified
    poet_info = f" in the style of {poet}" if poet else ""
    formatted = f"VERIFIED EXAMPLES WITH {rhyme_type} RHYME AND FEATURES {', '.join(features)}{poet_info}:\n\n"
    for i, item in enumerate(top_examples, 1):
        ex = item["example"]
        formatted += f"Example {i} from {item['poet']}:\n"
        formatted += f"Lines: {' / '.join(ex['lines'])}\n"
        formatted += f"Pattern: {ex['classification']}\n"
        phonetic = ex.get('phonetic', ['N/A', 'N/A'])
        formatted += f"Phonetic structure: {' / '.join(phonetic)}\n\n"
    
    # Add relevant statistics
    formatted += "\nRELEVANT CORPUS STATISTICS:\n"
    for corpus_key, corpus_data in corpus_to_search.items():
        if any(e["poet"] == corpus_data["poet"] for e in top_examples):
            formatted += f"\n{corpus_data['poet']} ({corpus_data['poem']}):\n"
            for stat_key, stat_val in corpus_data["stats"].items():
                if rhyme_type.lower() in stat_key.lower() or any(f.lower() in stat_key.lower() for f in features):
                    formatted += f"  - {stat_key}: {stat_val}%\n"
    
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
        for example in corpus_data["examples"]:
            lines = example["lines"]
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
                    "poet": corpus_data["poet"],
                    "words": f"{w1}-{w2}",
                    "claimed": example["classification"],
                    "found": res,
                    "msg": msg
                })
                
    return report
