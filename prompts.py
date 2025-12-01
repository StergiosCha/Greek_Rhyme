"""
Greek Rhyme Detection and Generation Prompts
Based on Topintzi et al. (2019) taxonomy
"""

ZERO_SHOT_STRUCTURED = """You are a Greek poetry rhyme analyzer. Your task is to identify rhyme patterns in Modern Greek poetry.

RHYME TAXONOMY:

1. **Position-based Classification:**
   - M (Masculine): Rhyme from final stressed vowel to line end
   - F2 (Feminine-2): Rhyme from penultimate stressed vowel to line end  
   - F3 (Feminine-3): Rhyme from antepenultimate stressed vowel to line end

2. **Complexity Features:**
   
   **RICH (onset consonants match):**
   - TR-S: Total rich with singleton onset (καλά - ξαλά)
   - TR-CC: Total rich with complex onset (αυγή - ναυγή)
   - PR-C1: Partial rich, first consonant matches (στόματα - σώματα)
   - PR-C2: Partial rich, second consonant matches (φοβερίζουν - τρίζουν)
   - PR-CC1/PR-CC2: Partial rich with complex onsets
   
   **IDV (Pre-rhyme vowel identity):**
   - Vowel before stressed syllable matches
   - IDV-2W: Matches across word boundaries
   
   **MOS (Mosaic):**
   - Rhyme domain crosses word boundaries
   
   **IMP (Imperfect):**
   - IMP-V: Stressed vowel differs (χάνετε - γίνετε)
   - IMP-C: Consonants differ (ξαφνίζει - τεχνίτη)
   - IMP-0F: Final consonant-zero alternation
   - IMP-0M: Medial consonant-zero alternation
   
   **COPY:**
   - Complete word/phrase repetition

ANALYSIS PROCEDURE:
1. Identify line-final stress position
2. Extract rhyme domain (from stressed vowel rightward)
3. Compare with other lines (scan 4-line window by default)
4. Classify by position (M/F2/F3) first
5. Then identify features (RICH, IDV, MOS, IMP, COPY)
6. Use phonetic similarity, NOT just orthography

For each rhyme pair, provide:
- Line numbers
- Rhyme domain in phonetic transcription
- Classification (e.g., M-TR-S-IDV, F2-MOS-IDV-2W, F3-IMP-V-PR-C1)
- Brief explanation

{rag_context}

POEM TO ANALYZE:
{text}
"""

ZERO_SHOT_ALGORITHM = """You are analyzing Greek poetry rhyme using this systematic approach:

DETECTION ALGORITHM:

1. **Syllabification**: Break each line into syllables
2. **Stress Location**: Identify primary stress position (final, penult, antepenult)
3. **Rhyme Domain Extraction**: 
   - Start from stressed vowel
   - Include all sounds to line end
   - May span word boundaries (MOSAIC)
4. **Comparison** (scan right-to-left):
   - Compare stressed vowels
   - Compare post-stress consonants
   - Check onset consonants before stressed vowel (RICH detection)
   - Check vowel before stress (IDV detection)
5. **Classification**: Apply hierarchical rules

CLASSIFICATION HIERARCHY:
First: Determine position type
- Final stress → M (Masculine)
- Penultimate stress → F2 (Feminine-2)
- Antepenultimate stress → F3 (Feminine-3)

Then: Check special features
- Onset matches? → RICH (TR-S, TR-CC, PR-C1, PR-C2)
- Pre-stress vowel matches? → IDV (or IDV-2W if across words)
- Crosses word boundary? → MOS
- Partial sound matching? → IMP (IMP-V, IMP-C, IMP-0F, IMP-0M)
- Identical repetition? → COPY

COMPARISON WINDOW: Default 4 lines, but scan entire stanza for patterns

{rag_context}

Apply this algorithmic method step-by-step to identify all rhymes in:

{text}
"""

FEW_SHOT = """You are a Greek rhyme pattern analyzer. Study these examples:

═══════════════════════════════════════════════════
EXAMPLE 1 - Masculine Rich Rhyme with Pre-vowel Identity:

Line 5: "Πάνω στην άμμο την ξανθή" [pa-no stin 'a-mo tin ksan-'Ti]
Line 8: "και σβήστηκε η γραφή" [ce 'zvi-sti-ce i Gra-'fi]

→ Classification: M-IDV

Reasoning:
- Both have stress on final syllable → Masculine (M)
- Rhyme domain: ['Ti] vs ['fi]
- Stressed vowels match: [i] = [i] ✓
- No post-stress consonants in either
- Pre-stress vowel: [A] in [ksAn-Ti] matches [A] in [GrA-fi] → IDV

═══════════════════════════════════════════════════
EXAMPLE 2 - Feminine-2 Mosaic with Cross-word Pre-vowel:

Line 6: "γράψαμε τ' όνομά της" ['Gra-psa-me 'to-no-'ma tis]
Line 7: "ωραία που φύσηξεν ο μπάτης" [o-'re-a pu 'fi-si-ksen o 'ba-tis]

→ Classification: F2-MOS-IDV-2W

Reasoning:
- Penultimate stress → F2
- Line 6 rhyme crosses words: ['ma tis]
- Line 7 rhyme: ['ba-tis]
- Stressed [a] = [a], following [tis] = [tis] ✓
- Rhyme spans word boundary in L6 → MOS
- Pre-vowel [O] matches across words [nO-ma / O ba] → IDV-2W

═══════════════════════════════════════════════════
EXAMPLE 3 - Masculine Imperfect (consonant variation):

Line 213: "ο μακρύς" [o ma-'kris]
Line 215: "στη θύρα ξαπλωμένο σκυλί" [sti 'Ti-ra ksa-plo-'me-no ski-'li]

→ Classification: M-IMP-C, M-IMP-0F

Reasoning:
- Final stress → M
- Rhyme domains: ['kris] vs ['li]
- Stressed vowels match: [i] = [i] ✓
- Post-stress: [s] vs [∅] → consonant differs
- Final consonant-zero alternation → IMP-0F
- Overall consonant imperfection → IMP-C

═══════════════════════════════════════════════════
EXAMPLE 4 - F3 with Imperfect Vowel and Partial Rich:

Line X: "στόματα" ['sto-ma-ta]
Line Y: "σώματα" ['so-ma-ta]

→ Classification: F3-IMP-V-PR-C1

Reasoning:
- Antepenultimate stress → F3
- Rhyme domains: ['sto-ma-ta] vs ['so-ma-ta]
- Stressed vowels differ: [o] ≠ [o] → IMP-V (actually they're different phonemes)
- Onset [st] vs [s]: first consonant [s] matches → PR-C1
- Rest of rhyme identical: [-ma-ta]

═══════════════════════════════════════════════════

{rag_context}

Now analyze the following Greek poem using the same systematic approach. For each rhyme pair:
1. Identify line numbers
2. Show phonetic transcription
3. Determine position classification (M/F2/F3)
4. Check for all features (RICH, IDV, MOS, IMP, COPY)
5. Provide final classification code

POEM:
{text}
"""

ZERO_SHOT_COT = """Analyze Greek poetry rhyme patterns using step-by-step reasoning.

SYSTEMATIC ANALYSIS FRAMEWORK:

For each potential rhyme pair, work through:

**STEP 1: Phonetic Analysis**
- Break line into syllables
- Locate primary stress (oxytone/paroxytone/proparoxytone)
- Transcribe sounds after stress

**STEP 2: Rhyme Domain Identification**
- Extract from stressed vowel to line end
- Note if domain crosses word boundaries
- Compare with other lines (4-line window default)

**STEP 3: Position Classification**
- Count syllables from stress to end
- 1 syllable from stress → M (Masculine)
- 2 syllables from stress → F2 (Feminine-2)
- 3 syllables from stress → F3 (Feminine-3)

**STEP 4: Feature Detection**
Check each feature systematically:
- Onset consonants match? → RICH (specify type: TR-S/TR-CC/PR-C1/PR-C2)
- Pre-stress vowel matches? → IDV (or IDV-2W if across words)
- Domain spans words? → MOS
- Vowels/consonants differ? → IMP (specify: IMP-V/IMP-C/IMP-0F/IMP-0M)
- Complete repetition? → COPY

**STEP 5: Classification Synthesis**
- Combine position + all applicable features
- Format: POSITION-FEATURE1-FEATURE2-...
- Example: M-TR-S-IDV or F2-MOS-IDV-2W-IMP-C

{rag_context}

Now analyze this poem, showing explicit reasoning for each rhyme:

{text}
"""

FEW_SHOT_COT = """Identify Greek rhyme patterns with explicit step-by-step analysis.

═══════════════════════════════════════════════════
WORKED EXAMPLE 1:

Lines:
L5: "Πάνω στην άμμο την ξανθή"
L8: "και σβήστηκε η γραφή"

REASONING PROCESS:

Step 1 - Syllabification & Stress:
L5: [pa-no stin 'a-mo tin ksan-'Ti] → stress on final 'Ti (oxytone)
L8: [ce 'zvi-sti-ce i Gra-'fi] → stress on final 'fi (oxytone)

Step 2 - Rhyme Domain Extraction:
L5: From stress rightward: ['Ti]
L8: From stress rightward: ['fi]

Step 3 - Sound Comparison:
- Stressed vowels: [i] = [i] ✓
- Post-stress consonants: none in both ✓
- RHYME CONFIRMED

Step 4 - Position Classification:
Stress on final syllable → MASCULINE (M)

Step 5 - Feature Analysis:
- Onset check: [T] vs [f] → different, not RICH
- Pre-stress vowel: [A] in [ksAn-'Ti] vs [A] in [GrA-'fi] ✓ → IDV
- No word-boundary crossing
- Perfect vowel/consonant match, not imperfect
- Not a repetition

**FINAL: M-IDV**

═══════════════════════════════════════════════════
WORKED EXAMPLE 2:

Lines:
L6: "γράψαμε τ' όνομά της"
L7: "ωραία που φύσηξεν ο μπάτης"

REASONING PROCESS:

Step 1 - Syllabification & Stress:
L6: ['Gra-psa-me 'to-no-'ma tis] → stress on 'ma (penultimate in phrase)
L7: [o-'re-a pu 'fi-si-ksen o 'ba-tis] → stress on 'ba (penultimate)

Step 2 - Rhyme Domain Extraction:
L6: ['ma tis] - NOTE: crosses word boundary!
L7: ['ba-tis]

Step 3 - Sound Comparison:
- Stressed vowels: [a] = [a] ✓
- Following material: [tis] = [tis] ✓
- RHYME CONFIRMED

Step 4 - Position Classification:
Stress on penultimate → FEMININE-2 (F2)

Step 5 - Feature Analysis:
- Onset check: [m] vs [b] → different, not RICH
- Pre-stress vowel: In L6 [nO-ma], in L7 [O ba] → [O] matches across words! → IDV-2W
- Word-boundary: L6 spans "ονομά + της" → MOS
- Perfect match within domain, not imperfect
- Not a repetition

**FINAL: F2-MOS-IDV-2W**

═══════════════════════════════════════════════════
WORKED EXAMPLE 3:

Lines:
L1: "στόματα" ['sto-ma-ta]
L2: "σώματα" ['so-ma-ta]

REASONING PROCESS:

Step 1 - Syllabification & Stress:
L1: ['sto-ma-ta] → stress on antepenult 'sto
L2: ['so-ma-ta] → stress on antepenult 'so

Step 2 - Rhyme Domain Extraction:
L1: ['sto-ma-ta]
L2: ['so-ma-ta]

Step 3 - Sound Comparison:
- Stressed vowels: [o] in L1, [o] in L2 (but check if same phoneme quality)
- Post-stress: [-ma-ta] = [-ma-ta] ✓
- NOTE: Vowel quality might differ slightly

Step 4 - Position Classification:
Stress on antepenultimate → FEMININE-3 (F3)

Step 5 - Feature Analysis:
- Onset check: [st] vs [s] → first consonant [s] matches → PR-C1 (partial rich)
- Pre-stress vowel: none (already at antepenult)
- No word-boundary crossing
- Stressed vowels may differ subtly → IMP-V (if phonetically distinct)
- Not a repetition

**FINAL: F3-PR-C1-IMP-V**

═══════════════════════════════════════════════════

{rag_context}

Now analyze the following poem using the same detailed five-step reasoning. Show your work for each rhyme pair:

{text}
"""

MOSAIC_ENHANCED_PROMPT = """Analyze Greek rhyme with PHONETIC PREPROCESSING for MOSAIC detection.

CRITICAL: MOSAIC (MOS) = rhyme crosses word boundaries.

{phonetic_analysis}

MOSAIC DETECTION:
1. Line ends with SHORT word (της/μου/σου/του/μας/σας/να/θα)?
2. Rhyme sound includes parts from BOTH last words?
3. Use PHONETICS, not spelling

TRUE MOSAIC EXAMPLES:
"όνομά της" [MA-tis] ~ "μπάτης" [BA-tis]  
→ Rhyme [MA tis] ~ [BA-tis] crosses "ονομά+της"

NOT MOSAIC:
"καρδιά" ~ "αγαπημένη" - single words

{rag_context}

POEM:
{text}

OUTPUT:
1. Line numbers
2. Phonetic (from preprocessing)
3. Word boundary check
4. Classification
5. Sound-based explanation
"""

GENERATION_PROMPT_TEMPLATE = """Generate Greek poetry lines with specific rhyme patterns.

TARGET SPECIFICATIONS:
- Rhyme type: {rhyme_type}
- Features: {features}
- Theme: {theme}
- Number of lines: {num_lines}

GENERATION CONSTRAINTS:

1. **Stress Placement:**
   - M (Masculine): Final syllable must be stressed
   - F2 (Feminine-2): Penultimate syllable must be stressed
   - F3 (Feminine-3): Antepenultimate syllable must be stressed

2. **Feature Requirements:**
   
   **RICH**: Match onset consonants before stressed vowel
   - TR-S: Single consonant matches exactly
   - TR-CC: Consonant cluster matches exactly
   - PR-C1/PR-C2: Partial match of onset consonants
   
   **IDV**: Pre-stress vowel must match
   - Can be within same word or across words (IDV-2W)
   
   **MOS (MOSAIC)**: CRITICAL - Rhyme MUST span word boundaries
   - The rhyme domain crosses from one word to the next word
   - Example: "όνομά της" [o-no-MÁ tis] rhymes with "ο μπάτης" [o ba-TIS]
     → The rhyme is: "μά της" (crosses words) ≈ "μπά της" sound
   - Example: "Δώσ' μου" [DOS mu] rhymes with "φως μου" [fos MU]
     → The rhyme spans: "ώς μου" (crosses "Δώσ'" + "μου")
   - NOT VALID: Single word endings like "ζηλεύω / ακολουθώ" (these are NOT mosaic)
   - MUST end line with short word (μου, σου, του, της, μας, σας, τους, να, θα, etc.)
   - The rhyme sound must include parts from BOTH the penultimate AND final word
   
   **IMP**: Allow imperfect rhyming
   - IMP-V: Stressed vowels can differ slightly
   - IMP-C: Some consonants can differ
   
   **PURE**: No special features, just basic rhyme match

3. **Quality Requirements:**
   - Maintain natural Modern Greek syntax
   - Ensure semantic coherence with theme
   - Use rich vocabulary and imagery
   - Avoid forced or awkward phrasing for rhyme
   - For MOSAIC: Use natural two-word combinations at line end

{rag_context}

IMPORTANT FOR MOSAIC RHYMES:
If MOS is requested, you MUST create rhymes that span word boundaries. Examples:
- "στο χέρι μου" [sto XÉ-ri mu] ~ "φέρε μου" [FÉ-re mu] (rhyme: "έ-ρι μου" / "έ-ρε μου")
- "την καρδιά μας" [tin kar-diÁ mas] ~ "η αγκαλιά μας" [i an-ga-liÁ sas] (rhyme: "διά μας" / "λιά σας")
- "δίνει φως μου" [Dí-ni fos mu] ~ "κι είναι δικό σου" [ki Í-ne di-KÓ su] (rhyme crosses words)

Generate the poem with phonetic annotations showing the rhyme pattern.
"""

def get_identification_prompt(text: str, strategy: str, rag_context: str = "", 
                             phonetic_analysis: str = "") -> str:
    """Get prompt for rhyme identification"""
    prompts = {
        "zero_shot_structured": ZERO_SHOT_STRUCTURED,
        "zero_shot_algorithm": ZERO_SHOT_ALGORITHM,
        "few_shot": FEW_SHOT,
        "zero_shot_cot": ZERO_SHOT_COT,
        "few_shot_cot": FEW_SHOT_COT,
        "mosaic_enhanced": MOSAIC_ENHANCED_PROMPT
    }
    
    rag_section = f"\n\nRELEVANT EXAMPLES FROM CORPUS:\n{rag_context}\n" if rag_context else ""
    
    if strategy == "mosaic_enhanced":
        return prompts[strategy].format(
            text=text, 
            rag_context=rag_section,
            phonetic_analysis=phonetic_analysis
        )
    
    return prompts[strategy].format(text=text, rag_context=rag_section)

def get_generation_prompt(theme: str, rhyme_type: str, features: list, 
                         num_lines: int, rag_context: str = "") -> str:
    """Get prompt for rhyme generation"""
    features_str = ", ".join(features) if features else "pure"
    rag_section = f"\n\nEXAMPLES FROM CORPUS WITH SIMILAR PATTERNS:\n{rag_context}\n" if rag_context else ""
    
    return GENERATION_PROMPT_TEMPLATE.format(
        rhyme_type=rhyme_type,
        features=features_str,
        theme=theme,
        num_lines=num_lines,
        rag_context=rag_section
    )