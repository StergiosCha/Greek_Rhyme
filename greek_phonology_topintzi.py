from greek_phonology import (
    detect_stress_position, 
    get_rhyme_part_and_onset, 
    CONSONANT_FEATURES
)
from typing import Dict, List, Tuple

def classify_rhyme_pair_topintzi(word1: str, word2: str) -> Dict:
    """
    Classify the rhyme between two words, including the 'Topintzi Variant' (IMP-0F).
    
    This variant strictly follows Topintzi et al. (2019) definition of IMP-0F,
    which allows Open vs Closed syllable rhymes (e.g. 'pistí' vs 'xarís').
    
    Returns:
        {
            'type': 'PURE' | 'RICH' | 'IMPERFECT' | 'NONE',
            'subtype': 'M' | 'F2' | 'F3',
            'details': '...'
        }
    """
    # 1. Get Stress and Phonetics
    s1 = detect_stress_position(word1)[0]
    s2 = detect_stress_position(word2)[0]
    
    if s1[1] != s2[1]:
        return {'type': 'NONE', 'reason': 'Stress mismatch'}
    stress_type = s1[1]
    
    # 2. Extract the "Rhyme Part"
    rp1, on1 = get_rhyme_part_and_onset(word1)
    rp2, on2 = get_rhyme_part_and_onset(word2)
    
    if not rp1 or not rp2:
        return {'type': 'UNKNOWN'}
        
    # Normalize: remove spaces
    rp1_norm = rp1.replace(' ', '')
    rp2_norm = rp2.replace(' ', '')
        
    # Check Pure Rhyme
    if rp1_norm == rp2_norm:
        if on1 and on2 and on1 == on2:
            return {'type': 'RICH', 'subtype': stress_type, 'onset': on1}
        return {'type': 'PURE', 'subtype': stress_type}
        
    # Check Imperfect Rhyme
    def get_cv_pattern(rp):
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
    
    # Check IMP-V (Stressed Vowel Mismatch)
    if len(rp1) > 1 and len(rp2) > 1:
        if vs1[1:] == vs2[1:] and cs1 == cs2 and vs1[0] != vs2[0]:
             if not cs1 and not vs1[1:]:
                 return {'type': 'NONE', 'reason': 'Single vowel mismatch (IMP-V rejected)'}
             return {'type': 'IMPERFECT', 'subtype': stress_type, 'imperfect_type': 'IMP-V', 'details': f"{vs1[0]}-{vs2[0]}"}

    # Check IMP-C (Consonant Mismatch)
    if vs1 == vs2:
        # Vowels match, Consonants differ.
        if cs1 != cs2:
            
            def is_subsequence(sub, main):
                it = iter(main)
                return all(c in it for c in sub)

            def are_consonants_compatible(c_list1, c_list2):
                # IMP-0F-TOPINTZI: Allow Open vs Closed syllable mismatch
                if not c_list1 or not c_list2:
                    return "IMP-0F-TOPINTZI"
                
                if len(c_list1) != len(c_list2):
                     if len(c_list1) < len(c_list2):
                         if is_subsequence(c_list1, c_list2): return "IMP-0"
                     else:
                         if is_subsequence(c_list2, c_list1): return "IMP-0"
                     return False
                
                for c1, c2 in zip(c_list1, c_list2):
                    if c1 == c2: continue
                    f1 = CONSONANT_FEATURES.get(c1)
                    f2 = CONSONANT_FEATURES.get(c2)
                    if not f1 or not f2: return False
                    
                    place_match = f1[0] == f2[0]
                    manner_match = f1[1] == f2[1]
                    
                    if place_match or manner_match: continue
                    
                    is_obstruent1 = f1[1] <= 2
                    is_obstruent2 = f2[1] <= 2
                    if is_obstruent1 != is_obstruent2: return False
                    continue
                    
                return "IMP-C"

            compatibility = are_consonants_compatible(cs1, cs2)
            
            if compatibility == "IMP-0":
                 return {'type': 'IMPERFECT', 'subtype': stress_type, 'imperfect_type': 'IMP-0', 'details': f"{cs1}-{cs2}"}
            elif compatibility == "IMP-0F-TOPINTZI":
                 return {'type': 'IMPERFECT', 'subtype': stress_type, 'imperfect_type': 'IMP-0F-TOPINTZI', 'details': f"{cs1}-{cs2}"}
            elif compatibility == "IMP-C":
                 return {'type': 'IMPERFECT', 'subtype': stress_type, 'imperfect_type': 'IMP-C', 'details': f"{cs1}-{cs2}"}
            else:
                 return {'type': 'NONE', 'reason': 'Incompatible consonants for IMP-C'}
    
    return {'type': 'NONE', 'subtype': stress_type, 'r1': rp1, 'r2': rp2}
