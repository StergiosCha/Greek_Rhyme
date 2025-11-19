"""
RAG System for Greek Rhyme Examples
Retrieves relevant examples from Greek Rhyme corpus
"""
import json
from typing import List, Dict
import re

# Sample rhyme corpus (in production, this would be loaded from database/vector store)
RHYME_CORPUS = {
    "solomos_imnos": {
        "poet": "Διονύσιος Σολωμός",
        "poem": "Ύμνος εις την Ελευθερία",
        "examples": [
            {
                "lines": ["Πάνω στην άμμο την ξανθή", "και σβήστηκε η γραφή"],
                "line_numbers": [5, 8],
                "classification": "M-IDV",
                "phonetic": ["ksan-'Ti", "Gra-'fi"],
                "features": ["M", "IDV"]
            },
            {
                "lines": ["γράψαμε τ' όνομά της", "ωραία που φύσηξεν ο μπάτης"],
                "line_numbers": [6, 7],
                "classification": "F2-MOS-IDV-2W",
                "phonetic": ["'to-no-'ma tis", "o 'ba-tis"],
                "features": ["F2", "MOS", "IDV-2W"]
            }
        ],
        "stats": {
            "total_lines": 632,
            "pure_M": 31.80,
            "pure_F2": 31.49,
            "rich": 10.45,
            "idv": 25.32,
            "imperfect": 0.0
        }
    },
    "mavilis_sonnets": {
        "poet": "Λορέντζος Μάβιλης",
        "poem": "23 Sonnets",
        "examples": [
            {
                "lines": ["Example line 1", "Example line 2"],
                "line_numbers": [1, 3],
                "classification": "F2-TR-S",
                "phonetic": ["'ka-la", "'xa-la"],
                "features": ["F2", "TR-S", "RICH"]
            }
        ],
        "stats": {
            "total_lines": 322,
            "pure_F2": 31.37,
            "rich": 56.94,
            "TR-S": 46.27,
            "PR-C2": 9.94
        }
    },
    "palamas_gypsy": {
        "poet": "Κωστής Παλαμάς",
        "poem": "Ο Δωδεκάλογος του Γύφτου",
        "examples": [
            {
                "lines": ["γιορτής", "ζωντανά"],
                "line_numbers": [183, 185],
                "classification": "M-IMP-V-IMP-0F",
                "phonetic": ["j\\or'tis", "zoda'na"],
                "features": ["M", "IMP-V", "IMP-0F"]
            }
        ],
        "stats": {
            "total_lines": 4260,
            "pure_M": 20.33,
            "pure_F2": 6.17,
            "imperfect_total": 48.92,
            "rich": 5.41,
            "idv": 10.62
        }
    },
    "karyotakis": {
        "poet": "Κ. Καρυωτάκης",
        "poem": "Ο Πόνος του Ανθρώπου και των Πραγμάτων",
        "examples": [
            {
                "lines": ["Line with M-IMP", "Line with M-IMP"],
                "classification": "M-IMP-C",
                "features": ["M", "IMP-C"]
            }
        ],
        "stats": {
            "total_lines": 265,
            "pure_M": 13.58,
            "pure_F2": 20.00,
            "M_imperfect": 20.75,
            "F2_idv": 24.15
        }
    }
}

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
                                 theme: str, top_k: int = 2) -> str:
    """
    Retrieve examples for generation task based on desired rhyme pattern
    """
    relevant_examples = []
    
    for corpus_key, corpus_data in RHYME_CORPUS.items():
        for example in corpus_data["examples"]:
            score = 0
            
            # Match rhyme type
            if rhyme_type in example["features"]:
                score += 5
            
            # Match additional features
            matched_features = len(set(features) & set(example["features"]))
            score += matched_features * 3
            
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
    
    formatted = f"EXAMPLES WITH {rhyme_type} RHYME AND FEATURES {', '.join(features)}:\n\n"
    for i, item in enumerate(top_examples, 1):
        ex = item["example"]
        formatted += f"Example {i} from {item['poet']}:\n"
        formatted += f"Lines: {' / '.join(ex['lines'])}\n"
        formatted += f"Pattern: {ex['classification']}\n"
        formatted += f"Phonetic structure: {' / '.join(ex['phonetic'])}\n\n"
    
    # Add relevant statistics
    formatted += "\nRELEVANT CORPUS STATISTICS:\n"
    for corpus_key, corpus_data in RHYME_CORPUS.items():
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

def get_corpus_stats(poet: str = None, rhyme_type: str = None) -> Dict:
    """Get statistics from corpus for specific poet or rhyme type"""
    stats = {}
    
    for corpus_key, corpus_data in RHYME_CORPUS.items():
        if poet and poet.lower() not in corpus_data["poet"].lower():
            continue
        
        stats[corpus_data["poet"]] = corpus_data["stats"]
    
    return stats
