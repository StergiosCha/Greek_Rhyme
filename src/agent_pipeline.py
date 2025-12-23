import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
import json

# Import our tools
from greek_phonology import classify_rhyme_pair, syllabify, detect_stress_position
from rag_system import get_generation_examples
from prompts import get_generation_prompt

@dataclass
class AgentResponse:
    content: str
    metadata: Dict[str, Any]

class VerificationTool:
    """
    Tool for objective phonetic verification of rhymes.
    Acts as the 'Ground Truth' for the agent.
    """
    def verify_rhyme(self, word1: str, word2: str, expected_type: str = None) -> Dict:
        """
        Verify if two words rhyme and how.
        """
        # Clean words
        w1 = word1.strip('.,;!?')
        w2 = word2.strip('.,;!?')
        
        result = classify_rhyme_pair(w1, w2)
        
        verification = {
            "is_valid": result['type'] != 'NONE',
            "phonetic_type": result['type'],
            "subtype": result.get('subtype'),
            "details": result.get('details', ''),
            "word1": w1,
            "word2": w2
        }
        
        if expected_type:
            # Check if it matches expectation
            # e.g. expected="RICH" -> result['type'] == 'RICH'
            if expected_type == "RICH" and result['type'] != "RICH":
                verification["match_expected"] = False
                verification["feedback"] = f"Expected RICH rhyme, but found {result['type']}."
            elif expected_type == "IMPERFECT" and result['type'] not in ("IMPERFECT", "NONE"):
                # If we wanted imperfect but got pure, maybe that's okay? 
                # But usually user wants specific style.
                verification["match_expected"] = True # Pure is better than imperfect?
            else:
                verification["match_expected"] = True
        
        return verification

class RhymeAgent:
    """
    LLM Agent wrapper.
    """
    def __init__(self, model_name: str = "gpt-4o", generate_callback = None):
        self.model_name = model_name
        self.generate_callback = generate_callback
        
    async def generate(self, prompt: str) -> str:
        """
        Call LLM to generate text.
        """
        if self.generate_callback:
            print(f"[{self.model_name}] Calling external LLM...")
            # callback should return (text, tokens)
            text, _ = await self.generate_callback(self.model_name, prompt)
            return text
            
        # Fallback to mock if no callback
        print(f"[{self.model_name}] Generating MOCK...")
        return "MOCK RESPONSE: \nLine 1: ... χαρά\nLine 2: ... φορά"

class AgentPipeline:
    """
    Orchestrates the generation and verification loop.
    """
    def __init__(self, model_name: str = "gpt-4o", generate_callback = None):
        self.generator = RhymeAgent(model_name, generate_callback)
        self.critic = RhymeAgent(model_name, generate_callback) # Could be different model
        self.verifier = VerificationTool()
        
    async def generate_poem(self, theme: str, rhyme_type: str, features: List[str], num_lines: int = 4, poet: str = None, use_rag: bool = True, use_verification: bool = True):
        """
        Generate a poem with optional verification loop.
        
        Args:
            use_verification: If True, use verification feedback loop (default). If False, generate once without verification.
        """
        print(f"--- Starting Pipeline for {theme} ({rhyme_type}, {features}) ---")
        if poet:
            print(f"--- Using poet style: {poet} ---")
        
        # 1. RAG Retrieval
        rag_examples = ""
        if use_rag:
            rag_examples = await get_generation_examples(rhyme_type, features, theme, poet=poet)
            print(f"RAG retrieved {len(rag_examples)} characters of examples")
            print("\n--- RAG EXAMPLES START ---")
            print(rag_examples)
            print("--- RAG EXAMPLES END ---\n")
        else:
            print("--- RAG Retrieval SKIPPED (use_rag=False) ---")
        
        # 2. Construct Prompt
        prompt = get_generation_prompt(theme, rhyme_type, features, num_lines, rag_examples)
        
        # Determine expected type - use the rhyme_type parameter!
        expected = rhyme_type  # This should be M, F2, or F3
        expected_stress = rhyme_type  # Preserve for stress checking
        
        # Override expected with feature-specific types if present
        # BUT keep expected_stress for stress verification!
        if "RICH" in features:
            expected = "RICH"
        elif "IMPERFECT" in features or "IMP" in features:
            expected = "IMPERFECT"
        
        # 3. Generation Loop (max 15 attempts if verification enabled, 1 if disabled)
        max_attempts = 15 if use_verification else 1
        for attempt in range(1, max_attempts + 1):
            print(f"\n--- Attempt {attempt}/{max_attempts} ---")
            
            # Generate draft
            draft = await self.generator.generate(prompt)
            print(f"Draft {attempt}:\n{draft[:200]}...")
            
            # If verification is disabled, return immediately
            if not use_verification:
                print("✓ Verification disabled - returning draft without validation")
                return {
                    "poem": draft,
                    "verification": {
                        "status": "VERIFICATION DISABLED",
                        "message": "Poem generated without verification loop"
                    },
                    "attempts": 1
                }
            
            # 4. Extraction & Verification
            lines = [l.strip() for l in draft.split('\n') if l.strip() and not l.startswith('MOCK')]
            
            # Filter and CLEAN lines - strip metadata but keep Greek poetry
            clean_lines = []
            
            def is_greek(text):
                """Check if text contains Greek characters"""
                import re
                # Greek unicode range: \u0370-\u03FF and \u1F00-\u1FFF
                return bool(re.search(r'[\u0370-\u03FF\u1F00-\u1FFF]', text))

            for line in lines:
                original_line = line
                
                # Strip leading numbers (1. 2. 3. etc.)
                import re
                line = re.sub(r'^\d+\.\s*', '', line)
                
                # Strip markdown bold/italic
                line = line.replace('**', '').replace('*', '')
                
                # Strip phonetic annotations in parentheses or brackets at end of line
                line = re.sub(r'\s*[\(\[].*?[\)\]]\s*$', '', line)
                
                # Strip leading/trailing whitespace
                line = line.strip()
                
                # NOW apply filters on the CLEANED line
                
                # Skip if too short after cleaning
                if len(line) < 5: # Relaxed length check slightly
                    continue
                    
                # Skip if it's a markdown header
                if line.startswith('#'):
                    continue
                    
                # Skip if it still has parentheses/brackets (mid-line annotations)
                if '(' in line or ')' in line or '[' in line or ']' in line:
                    continue
                
                # Skip if NO Greek characters
                if not is_greek(line):
                    continue
                
                # Skip lines with English words (metadata) - secondary check
                english_words = ['rhyme', 'phonetic', 'annotation', 'poem', 'theme', 'verification', 'pattern', 'lines', 'with']
                if any(word.lower() in line.lower() for word in english_words):
                    continue
                
                # Skip obvious separators
                if line.strip() in ['---', '***', '==='] or line.strip().startswith('---'):
                    continue
                
                # If it passed all filters, keep it
                clean_lines.append(line)
            
            lines = clean_lines
            
            if len(lines) < 2:
                return {"error": f"Draft too short (only {len(lines)} lines)", "poem": draft}
            
            # Debug: Show what lines we're actually checking
            print(f"Lines to verify ({len(lines)} total):")
            for i, line in enumerate(lines, 1):
                print(f"  {i}. {line[:60]}{'...' if len(line) > 60 else ''}")
            
            # Verify ALL couplets
            all_valid = True
            verifications = []
            failed_pairs = []
            
            # Check consecutive pairs (assuming couplet structure)
            for i in range(0, len(lines) - 1, 2):
                if i + 1 >= len(lines):
                    break
                
                # Use extract_rhyme_domain to handle clitics and multi-word rhyme domains
                from greek_phonology import extract_rhyme_domain
                rd1 = extract_rhyme_domain(lines[i])
                rd2 = extract_rhyme_domain(lines[i+1])
                
                # Extract the rhyme domain (handles clitics like "μου", "της", etc.)
                w1 = rd1['rhyme_domain'].strip('*').strip('**')
                w2 = rd2['rhyme_domain'].strip('*').strip('**')
                
                verification = self.verifier.verify_rhyme(w1, w2, expected_type=expected)
                
                # Additional check: if MOSAIC was requested, verify it's actually mosaic
                is_feature_match = True
                feature_error = None
                
                if "MOS" in features or "MOSAIC" in features:
                    # Check if this is actually a mosaic rhyme
                    from greek_phonology import analyze_mosaic_pattern
                    mosaic_check = analyze_mosaic_pattern(lines[i], lines[i+1])
                    if not mosaic_check['mosaic_candidate']:
                        is_feature_match = False
                        feature_error = f"MOSAIC requested but '{w1}' / '{w2}' is not a mosaic rhyme (type: {verification['phonetic_type']})"
                
                # Check for rhyme quality (PURE, RICH, IMPERFECT)
                # If any quality is requested, ONLY accept that exact type
                if "pure" in features and is_feature_match:
                    rhyme_type = verification['phonetic_type']
                    if rhyme_type != 'PURE':
                        is_feature_match = False
                        feature_error = f"PURE requested but '{w1}' / '{w2}' is {rhyme_type}"
                
                if "RICH" in features and is_feature_match:
                    rhyme_type = verification['phonetic_type']
                    if rhyme_type != 'RICH':
                        is_feature_match = False
                        feature_error = f"RICH requested but '{w1}' / '{w2}' is {rhyme_type}"
                
                if ("IMPERFECT" in features or "IMP" in features) and is_feature_match:
                    rhyme_type = verification['phonetic_type']
                    if rhyme_type != 'IMPERFECT':
                        is_feature_match = False
                        feature_error = f"IMPERFECT requested but '{w1}' / '{w2}' is {rhyme_type}"
                
                # Check for Stress Position (F1, F2, F3)
                # F1 = Oxytone (M), F2 = Paroxytone, F3 = Proparoxytone
                requested_stress = None
                
                # Check features first
                if "F1" in features or "M" in features: requested_stress = "M"
                elif "F2" in features: requested_stress = "F2"
                elif "F3" in features: requested_stress = "F3"
                
                # If not in features, check the expected_stress (rhyme_type)
                if not requested_stress and expected_stress:
                    if expected_stress in ["F1", "M"]: requested_stress = "M"
                    elif expected_stress == "F2": requested_stress = "F2"
                    elif expected_stress == "F3": requested_stress = "F3"
                
                
                if requested_stress and is_feature_match:
                    # Check stress of both words
                    from greek_phonology import detect_stress_position
                    s1 = detect_stress_position(w1)
                    s2 = detect_stress_position(w2)
                    
                    print(f"DEBUG: Stress check for '{w1}' / '{w2}'")
                    print(f"  Requested: {requested_stress}")
                    print(f"  Found: {s1} / {s2}")
                    
                    # s1 is list of tuples like [(1, 'M')] or [(3, 'F3')]
                    # We need to find if any valid stress matches requested
                    def matches_stress(stress_info, req):
                        for _, code in stress_info:
                            if code == req: return True
                            if req == "F1" and code == "M": return True # Handle F1/M equivalence
                            if req == "M" and code == "F1": return True
                        return False

                    if not (matches_stress(s1, requested_stress) and matches_stress(s2, requested_stress)):
                        is_feature_match = False
                        feature_error = f"Stress mismatch: Expected {requested_stress}, found {s1}/{s2}"
                        print(f"  REJECTED: {feature_error}")
                    else:
                        print(f"  ACCEPTED: Stress matches")
                else:
                    if not requested_stress:
                        print(f"DEBUG: No stress check - requested_stress is None (expected={expected}, features={features})")

                # Check for IDV (Identical Pre-stress Vowel)
                if "IDV" in features and is_feature_match:
                    # Helper to find pre-stress vowel
                    def get_pre_stress_vowel(word):
                        # Simple heuristic: remove stress accent, find vowel before the stressed syllable
                        # This is hard without full syllabification.
                        # Let's use a simplified approach:
                        # 1. Find index of stressed vowel (accented char)
                        # 2. Look backwards for the next vowel
                        accent_chars = 'άέήίόύώ'
                        vowels = 'αεηιουωάέήίόύώ'
                        
                        stress_idx = -1
                        for i, c in enumerate(word):
                            if c in accent_chars:
                                stress_idx = i
                                break # Use first accent found? Or last? Greek usually has one.
                        
                        if stress_idx == -1: return None
                        
                        start_scan = stress_idx - 1
                        # Scan backwards
                        for i in range(start_scan, -1, -1):
                            char = word[i].lower()
                            # Synizesis handling
                            if i == start_scan and char == 'ι':
                                continue
                            
                            # Handle diphthongs 'αυ', 'ευ' where 'υ' is consonant [f/v]
                            # If we find 'υ', check if previous char is 'α' or 'ε'.
                            # If so, 'υ' is part of the diphthong, so we skip it to find the nucleus ('α' or 'ε').
                            if char == 'υ' and i > 0:
                                prev_char = word[i-1].lower()
                                if prev_char in ['α', 'ε']:
                                    continue
                                
                            if char in vowels:
                                return char
                        return None

                    v1 = get_pre_stress_vowel(w1)
                    v2 = get_pre_stress_vowel(w2)
                    
                    # Map vowels to phonetic sounds (e.g. η, ι, υ -> i)
                    phonetic_map = {
                        'α': 'a', 'ά': 'a',
                        'ε': 'e', 'έ': 'e', 'αι': 'e',
                        'η': 'i', 'ή': 'i', 'ι': 'i', 'ί': 'i', 'υ': 'i', 'ύ': 'i', 'ει': 'i', 'οι': 'i',
                        'ο': 'o', 'ό': 'o', 'ω': 'o', 'ώ': 'o',
                        'ου': 'u'
                    }
                    # Note: Digraphs like 'ει' are hard to catch with simple char scan.
                    # But for now, simple char mapping is better than nothing.
                    
                    def normalize_vowel(v):
                        return phonetic_map.get(v, v)

                    if v1 and v2:
                        if normalize_vowel(v1) != normalize_vowel(v2):
                            is_feature_match = False
                            feature_error = f"IDV requested but pre-stress vowels differ: '{v1}' vs '{v2}'"
                    else:
                        # If no pre-stress vowel (e.g. word starts with stress), IDV is impossible?
                        # Or maybe it matches if BOTH have no pre-stress vowel?
                        if v1 != v2:
                            is_feature_match = False
                            feature_error = f"IDV requested but pre-stress vowel structure differs."

                # Check for Identical Words (COPY)
                # Unless COPY is requested, we should reject identical words
                is_copy = w1.lower() == w2.lower()
                if is_copy and "COPY" not in features:
                    is_feature_match = False
                    feature_error = f"Identical words '{w1}' / '{w2}' (COPY) are not allowed unless requested."

                verifications.append({
                    "pair": (i+1, i+2),
                    "words": f"{w1} / {w2}",
                    "result": verification,
                    "feature_match": is_feature_match
                })
                
                # Check if rhyme type matches expectation (e.g. RICH)
                matches_expected_type = verification.get('match_expected', True)
                
                if not verification['is_valid'] or not is_feature_match or not matches_expected_type:
                    all_valid = False
                    
                    if feature_error:
                        error_msg = feature_error
                    elif not matches_expected_type:
                        error_msg = verification.get('feedback', f"Rhyme type mismatch (expected {expected})")
                    else:
                        error_msg = f"No rhyme detected between '{w1}' and '{w2}'"
                        
                    failed_pairs.append({
                        "lines": (i+1, i+2),
                        "words": f"{w1} / {w2}",
                        "error": error_msg
                    })
            
            # Count fully valid pairs (phonetic + feature + stress + not copy)
            valid_count = 0
            for v in verifications:
                # We need to check the same conditions as the loop above
                # But we didn't store the "matches_expected_type" in 'v' explicitly
                # Let's rely on the fact that if it failed, it's in failed_pairs?
                # No, failed_pairs is a separate list.
                
                # Let's just count how many are NOT in failed_pairs
                pass 
            
            # Better way:
            valid_count = len(verifications) - len(failed_pairs)
            print(f"Verification: {valid_count}/{len(verifications)} pairs fully valid")
            
            # 5. If all valid, return success
            if all_valid:
                mosaic_note = " (MOSAIC requested)" if ("MOS" in features or "MOSAIC" in features) else ""
                print(f"✓ All rhymes valid!{mosaic_note}")
                return {
                    "poem": draft,
                    "verification": {
                        "status": f"✓ ALL RHYMES VALID{mosaic_note}",
                        "pairs_checked": len(verifications),
                        "pairs": [
                            {
                                "lines": v["pair"],
                                "words": v["words"],
                                "rhyme_type": v["result"]["phonetic_type"],
                                "valid": v["result"]["is_valid"]
                            }
                            for v in verifications
                        ]
                    },
                    "attempts": attempt
                }
            
            # 6. If invalid and not last attempt, retry with feedback
            if attempt < max_attempts:
                print(f"✗ {len(failed_pairs)} pair(s) failed. Retrying with feedback...")
                
                # Construct detailed feedback
                feedback = "\n\nYOUR PREVIOUS ATTEMPT HAD SOME ERRORS.\n"
                
                # Identify valid pairs to keep
                failed_indices = [f['lines'] for f in failed_pairs]
                valid_pairs = [v for v in verifications if v['pair'] not in failed_indices]
                
                if valid_pairs:
                    feedback += "\n✅ THE FOLLOWING PAIRS ARE VALID - YOU MUST KEEP THEM EXACTLY AS IS:\n"
                    feedback += "Do NOT change a single character in these lines. Copy them verbatim.\n"
                    for v in valid_pairs:
                        # Get full line text
                        # v['pair'] is (1, 2) etc. (1-based)
                        idx1 = v['pair'][0] - 1
                        idx2 = v['pair'][1] - 1
                        line1_text = lines[idx1] if idx1 < len(lines) else ""
                        line2_text = lines[idx2] if idx2 < len(lines) else ""
                        
                        feedback += f"Line {v['pair'][0]}: {line1_text}\n"
                        feedback += f"Line {v['pair'][1]}: {line2_text}\n"
                        feedback += f"(Status: Valid {v['result']['phonetic_type']} rhyme: {v['words']})\n\n"
                
                feedback += "\n❌ THE FOLLOWING PAIRS FAILED - YOU MUST FIX THEM:\n"
                for fail in failed_pairs:
                    lines_str = f"{fail['lines'][0]}-{fail['lines'][1]}"
                    feedback += f"- Lines {lines_str}: {fail['error']}\n"
                
                feedback += "\nINSTRUCTION: Rewrite the poem. COPY the valid lines exactly as shown above. ONLY rewrite the failed lines to fix the rhymes.\n"
                
                feedback += f"\nREMINDER: You MUST create {rhyme_type} rhymes (penultimate/final syllable stress) where the rhyme domains match phonetically.\n"
                feedback += "IMPORTANT: The final words must actually RHYME. Check the stressed vowel and following sounds match!\n"
                feedback += f"Expected rhyme type: {expected}\n\n"
                feedback += "Please try again and ensure ALL couplets have valid rhymes.\n"
                
                # Add feedback to prompt for retry
                prompt = prompt + feedback
            else:
                # Last attempt failed, return with detailed error
                print(f"✗ Failed after {max_attempts} attempts")
                return {
                    "poem": draft,
                    "verification": {
                        "status": f"✗ FAILED - {len(failed_pairs)}/{len(verifications)} pairs invalid",
                        "pairs_checked": len(verifications),
                        "failed_pairs": [
                            {
                                "lines": f["lines"],
                                "words": f["words"],
                                "error": f["error"]
                            }
                            for f in failed_pairs
                        ],
                        "all_pairs": [
                            {
                                "lines": v["pair"],
                                "words": v["words"],
                                "rhyme_type": v["result"]["phonetic_type"],
                                "valid": v["result"]["is_valid"]
                            }
                            for v in verifications
                        ]
                    },
                    "attempts": attempt,
                    "error": f"Could not generate valid rhymes after {max_attempts} attempts"
                }
        
        # Should never reach here
        return {"error": "Unexpected end of generation loop"}
