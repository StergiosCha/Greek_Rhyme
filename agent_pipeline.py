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
        
    async def generate_poem(self, theme: str, rhyme_type: str, features: List[str], num_lines: int = 4, poet: str = None):
        """
        Generate a poem with verification loop.
        """
        print(f"--- Starting Pipeline for {theme} ({rhyme_type}, {features}) ---")
        if poet:
            print(f"--- Using poet style: {poet} ---")
        
        # 1. RAG Retrieval
        rag_examples = await get_generation_examples(rhyme_type, features, theme, poet=poet)
        print(f"RAG retrieved {len(rag_examples)} characters of examples")
        
        # 2. Construct Prompt
        prompt = get_generation_prompt(theme, rhyme_type, features, num_lines, rag_examples)
        
        # Determine expected type
        expected = "PURE"
        if "RICH" in features:
            expected = "RICH"
        elif "IMPERFECT" in features or "IMP" in features:
            expected = "IMPERFECT"
        
        # 3. Generation Loop (max 3 attempts)
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            print(f"\n--- Attempt {attempt}/{max_attempts} ---")
            
            # Generate draft
            draft = await self.generator.generate(prompt)
            print(f"Draft {attempt}:\n{draft[:200]}...")
            
            # 4. Extraction & Verification
            lines = [l.strip() for l in draft.split('\n') if l.strip() and not l.startswith('MOCK')]
            
            # Filter and CLEAN lines - strip metadata but keep Greek poetry
            clean_lines = []
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
                if len(line) < 10:
                    continue
                    
                # Skip if it's a markdown header
                if line.startswith('#'):
                    continue
                    
                # Skip if it still has parentheses/brackets (mid-line annotations)
                if '(' in line or ')' in line or '[' in line or ']' in line:
                    continue
                
                # Skip if starts with non-Greek character
                if not line[0].isalpha():
                    continue
                
                # Skip lines with English words (metadata)
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
                verifications.append({
                    "pair": f"{i+1}-{i+2}",
                    "words": f"{w1} / {w2}",
                    "result": verification
                })
                
                if not verification['is_valid']:
                    all_valid = False
                    failed_pairs.append({
                        "lines": f"{i+1}-{i+2}",
                        "words": f"{w1} / {w2}",
                        "error": f"No rhyme detected between '{w1}' and '{w2}'"
                    })
            
            print(f"Verification: {len([v for v in verifications if v['result']['is_valid']])}/{len(verifications)} pairs valid")
            
            # 5. If all valid, return success
            if all_valid:
                print("✓ All rhymes valid!")
                return {
                    "poem": draft,
                    "verification": {
                        "status": "✓ ALL RHYMES VALID",
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
                feedback = "\n\nYOUR PREVIOUS ATTEMPT HAD RHYME ERRORS:\n\n"
                for fail in failed_pairs:
                    feedback += f"- Lines {fail['lines']}: {fail['error']}\n"
                
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
