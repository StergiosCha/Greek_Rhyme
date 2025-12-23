"""
Verification utilities for rhyme identification
Analyzes the POEM ITSELF to find rhymes, then compares with LLM output
"""

import re
from typing import Dict, List, Tuple
from greek_phonology import classify_rhyme_pair, extract_rhyme_domain


def find_all_rhymes_in_poem(poem_text: str, max_distance: int = 20) -> List[Dict]:
    """
    Analyze the poem directly to find ALL valid rhyme pairs.
    This is the GROUND TRUTH based on phonological rules.
    Detects ALL features: MOSAIC, IDV, RICH subtypes, IMPERFECT subtypes, COPY
    
    Args:
        poem_text: The poem text
        max_distance: Maximum line distance to check (default 20 lines)
    
    """
    from greek_phonology import analyze_mosaic_pattern, extract_pre_rhyme_vowel
    
    lines = [l.strip() for l in poem_text.split('\n') if l.strip()]
    
    valid_rhymes = []
    
    # Check all pairs within max_distance
    for i in range(len(lines)):
        for j in range(i + 1, min(i + max_distance + 1, len(lines))):
            # Extract rhyme domains
            rd1 = extract_rhyme_domain(lines[i])
            rd2 = extract_rhyme_domain(lines[j])
            
            w1 = rd1['rhyme_domain'].strip('*·.').strip()
            w2 = rd2['rhyme_domain'].strip('*·.').strip()
            
            # Classify the pair
            result = classify_rhyme_pair(w1, w2)
            
            # If it's a valid rhyme, add it
            if result.get('type') not in ['NONE', 'UNKNOWN']:
                features = []
                
                # 1. Check for MOSAIC
                mosaic_check = analyze_mosaic_pattern(lines[i], lines[j])
                if mosaic_check.get('mosaic_candidate', False):
                    features.append('MOSAIC')
                
                # 2. Check for IDV (Identical Pre-rhyme Vowel)
                v1 = extract_pre_rhyme_vowel(w1)
                v2 = extract_pre_rhyme_vowel(w2)
                if v1 and v2:
                    # Phonetic normalization
                    phonetic_map = {
                        'α': 'a', 'ά': 'a',
                        'ε': 'e', 'έ': 'e',
                        'η': 'i', 'ή': 'i', 'ι': 'i', 'ί': 'i', 'υ': 'i', 'ύ': 'i',
                        'ο': 'o', 'ό': 'o', 'ω': 'o', 'ώ': 'o',
                    }
                    if phonetic_map.get(v1, v1) == phonetic_map.get(v2, v2):
                        features.append('IDV')
                
                # 3. Check for COPY (identical words)
                if w1.lower() == w2.lower():
                    features.append('COPY')
                
                # 4. Add RICH subtype if present (from classify_rhyme_pair details)
                rhyme_type = result.get('type')
                if rhyme_type == 'RICH':
                    # classify_rhyme_pair already categorizes RICH subtypes
                    # The subtype will show if it's TR-S, TR-CC, or PR-C
                    pass  # Already in rhyme_type
                
                # 5. Add IMPERFECT subtype if present
                if rhyme_type == 'IMPERFECT':
                    # classify_rhyme_pair provides details like IMP-V, IMP-C, IMP-0F, IMP-0M
                    # This is in the 'details' field
                    details = result.get('details', '')
                    if 'IMP-V' in details or 'vowel' in details.lower():
                        features.append('IMP-V')
                    elif 'IMP-C' in details or 'consonant' in details.lower():
                        features.append('IMP-C')
                    elif 'IMP-0' in details:
                        if 'final' in details.lower():
                            features.append('IMP-0F')
                        elif 'medial' in details.lower():
                            features.append('IMP-0M')
                        else:
                            features.append('IMP-0')
                
                valid_rhymes.append({
                    'line1': i + 1,  # 1-indexed
                    'line2': j + 1,
                    'word1': w1,
                    'word2': w2,
                    'rhyme_type': rhyme_type,
                    'rhyme_subtype': result.get('subtype', ''),
                    'features': features,
                    'details': result.get('details', ''),
                    'is_valid': True
                })
    
    return valid_rhymes


def parse_llm_rhyme_output(llm_output: str) -> Dict:
    """
    Parse LLM output to extract rhyme classification (e.g., M-PURE, F2-MOS)
    """
    # Look for explicit classification line
    # Matches: "**Classification**: M-PURE", "Type: F2-MOSAIC", "Classification: **F2-PURE**"
    # Robust regex: keyword, optional garbage, colon, optional garbage, CODE
    class_pattern = r'(?:Classification|Type|Code|Synthesis).*?:\s*(?:\*\*)?([A-Za-z0-9\-\+]+)(?:\*\*)?'
    match = re.search(class_pattern, llm_output, re.IGNORECASE)
    
    classification = None
    if match:
        classification = match.group(1).upper()
    else:
        # Fallback: Look for pattern in the text like "-> M-IDV" or "Result: F3-IMP"
        # Also handles bolding/markdown
        fallback_pattern = r'(?:→|Result|Pattern)(?:\*\*|:)?\s*[:]?\s*([A-Za-z0-9\-\+]+)'
        match = re.search(fallback_pattern, llm_output, re.IGNORECASE)
        if match:
            classification = match.group(1).upper()
    
    if not classification:
        return {'rhyme_type': None, 'features': []}
    
    # Parse the classification string
    parts = classification.split('-')
    if not parts:
        return {'rhyme_type': None, 'features': []}
    
    # First part is always rhyme type (M, F2, F3)
    rhyme_type = parts[0]
    features = parts[1:] if len(parts) > 1 else []
    
    # Clean up features
    clean_features = []
    # Map common feature names
    feature_map = {
        'MOS': 'MOSAIC',
        'IMP': 'IMPERFECT',
        'TR': 'RICH', 'PR': 'RICH', 'RICH': 'RICH',
        'IDV': 'IDV',
        'PURE': 'PURE',
        'COPY': 'COPY'
    }
    
    for f in features:
        # Check against map keys
        mapped = False
        for key, value in feature_map.items():
            if key in f:
                clean_features.append(value)
                mapped = True
                break
        if not mapped:
             # Just keep what we found if not mapped, removing generic codes
             if len(f) > 1:
                 clean_features.append(f)
    
    # Deduplicate
    clean_features = sorted(list(set(clean_features)))
    
    # If no features found, assume BASIC/PURE if not empty
    # But usually PURE is explicit. If features list is empty, it's basic.
    
    return {
        'rhyme_type': rhyme_type,
        'features': clean_features,
        'raw_code': classification
    }



def verify_identification_output(llm_output: str, original_text: str) -> Dict:
    """
    Analyze the poem ITSELF to find ground truth rhymes,
    then show them to the LLM for reflection.
    
    SIMPLIFIED: We don't try to parse what LLM claimed.
    We just show the ground truth and let LLM compare.
    """
    # Find ALL valid rhymes in the poem (GROUND TRUTH)
    ground_truth = find_all_rhymes_in_poem(original_text)
    
    # Create summary showing ground truth
    summary_lines = []
    summary_lines.append(f"PHONOLOGICAL ANALYSIS (GROUND TRUTH):")
    summary_lines.append(f"Found {len(ground_truth)} valid rhyme pair(s) in the poem:")
    summary_lines.append(f"")
    
    if ground_truth:
        for gt in ground_truth:
            # Build classification string
            classification = f"{gt['rhyme_type']}, {gt['rhyme_subtype']}"
            
            # Add features if present
            if gt.get('features'):
                features_str = ', '.join(gt['features'])
                classification += f", {features_str}"
            
            summary_lines.append(
                f"  ✓ Lines {gt['line1']}-{gt['line2']}: {gt['word1']} / {gt['word2']} "
                f"({classification})"
            )
    else:
        summary_lines.append("  (No valid rhymes found)")
    
    summary_lines.append(f"")
    summary_lines.append(f"Please compare this ground truth with your analysis.")
    summary_lines.append(f"Identify any differences:") 
    summary_lines.append(f"  - Did you correctly identify all rhyme pairs?")
    summary_lines.append(f"  - Did you correctly classify the rhyme types (M/F2/F3)?")
    summary_lines.append(f"  - Did you correctly classify the rhyme quality (PURE/RICH/IMPERFECT)?")
    summary_lines.append(f"  - Did you correctly identify MOSAIC rhymes (rhyme domain spans word boundaries)?")
    summary_lines.append(f"  - Did you claim any pairs that don't actually rhyme?")
    
    return {
        'ground_truth_rhymes': ground_truth,
        'verification_summary': '\n'.join(summary_lines)
    }

