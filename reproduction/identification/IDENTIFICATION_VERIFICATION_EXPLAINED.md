# How Identification with Verification Works

## Overview

The **identification with verification** system analyzes existing Greek poems to find rhymes. It uses a **3-step process** that combines LLM analysis with symbolic phonological validation.

---

## The 3-Step Process

### Step 1: LLM Initial Analysis
The LLM reads the poem and identifies rhyme pairs.

**Input**: Greek poem text
```
Στη θάλασσα η καρδιά μου πάει
και στα κύματα χορεύει
με τον άνεμο που φυσάει
και το φως που λαμπυρίζει
```

**LLM Output**:
```
Rhyme Scheme: ABAB
- Lines 1 & 3: πάει / φυσάει (M rhyme, PURE)
- Lines 2 & 4: χορεύει / λαμπυρίζει (F2 rhyme, IMPERFECT)
```

---

### Step 2: Symbolic Verification (Ground Truth)

The system uses **phonological rules** (not LLM) to find ALL valid rhymes in the poem.

#### 2a. Find Ground Truth Rhymes
```python
def find_all_rhymes_in_poem(poem_text: str) -> List[Dict]:
    """
    Analyze poem using symbolic rules to find ALL valid rhymes.
    This is the GROUND TRUTH.
    """
    lines = poem_text.split('\n')
    valid_rhymes = []
    
    # Check all line pairs
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            # Extract rhyme domains
            rd1 = extract_rhyme_domain(lines[i])  # e.g., "πάει"
            rd2 = extract_rhyme_domain(lines[j])  # e.g., "φυσάει"
            
            # Classify using phonological rules
            result = classify_rhyme_pair(rd1, rd2)
            
            # If valid rhyme, add to ground truth
            if result['type'] != 'NONE':
                valid_rhymes.append({
                    'line1': i+1,
                    'line2': j+1,
                    'words': (rd1, rd2),
                    'rhyme_type': result['type'],  # PURE, RICH, IMPERFECT
                    'rhyme_subtype': result['subtype']  # M, F2, F3
                })
    
    return valid_rhymes
```

**Ground Truth Output**:
```
Found 2 valid rhyme pairs:
1. Lines 1-3: πάει / φυσάει (PURE, M)
2. Lines 2-4: χορεύει / λαμπυρίζει (IMPERFECT-V, F2)
```

#### 2b. Parse LLM Claims
```python
def parse_llm_rhyme_output(llm_output: str) -> List[Dict]:
    """
    Extract line pairs that LLM claimed rhyme.
    Uses regex to find "Lines 1 & 3", "Lines 2-4", etc.
    """
    pairs = []
    pattern = r'[Ll]ines?\s*(\d+)\s*(?:&|and|[-–—])\s*(\d+)'
    
    for match in re.finditer(pattern, llm_output):
        pairs.append({
            'line1': int(match.group(1)),
            'line2': int(match.group(2))
        })
    
    return pairs
```

**LLM Claims**:
```
Claimed 2 pairs:
1. Lines 1-3
2. Lines 2-4
```

#### 2c. Compare LLM vs Ground Truth
```python
def verify_identification_output(llm_output: str, poem_text: str) -> Dict:
    """
    Compare LLM claims against ground truth.
    Calculate Precision, Recall, F1.
    """
    ground_truth = find_all_rhymes_in_poem(poem_text)
    llm_claimed = parse_llm_rhyme_output(llm_output)
    
    true_positives = []   # LLM correctly identified
    false_positives = []  # LLM incorrectly claimed
    false_negatives = []  # LLM missed
    
    # Match LLM claims to ground truth
    for claimed in llm_claimed:
        matched = False
        for gt in ground_truth:
            if claimed['line1'] == gt['line1'] and claimed['line2'] == gt['line2']:
                true_positives.append(gt)
                matched = True
                break
        
        if not matched:
            false_positives.append(claimed)
    
    # Find missed rhymes
    for gt in ground_truth:
        if gt not in true_positives:
            false_negatives.append(gt)
    
    # Calculate metrics
    precision = len(true_positives) / (len(true_positives) + len(false_positives))
    recall = len(true_positives) / (len(true_positives) + len(false_negatives))
    f1 = 2 * precision * recall / (precision + recall)
    
    return {
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }
```

**Verification Results**:
```
GROUND TRUTH: 2 valid rhyme pairs found
LLM CLAIMED: 2 pairs

✓ TRUE POSITIVES: 2 (correctly identified)
✗ FALSE POSITIVES: 0 (incorrectly claimed)
✗ FALSE NEGATIVES: 0 (missed)

Precision: 100.0%
Recall: 100.0%
F1 Score: 100.0%

--- TRUE POSITIVES (LLM got these right) ---
  ✓ Lines 1-3: πάει / φυσάει (PURE, M)
  ✓ Lines 2-4: χορεύει / λαμπυρίζει (IMPERFECT, F2)
```

---

### Step 3: LLM Reflection & Correction

The verification results are sent back to the LLM for reflection.

**Feedback Prompt**:
```
You previously analyzed this Greek poem for rhymes:

[poem text]

Your analysis was:
[LLM initial output]

PHONOLOGICAL VERIFICATION RESULTS:
[verification summary with TP/FP/FN]

Please review the verification results and provide a corrected analysis that:
1. Acknowledges which rhymes you correctly identified
2. Explains any rhymes you missed
3. Corrects any false rhymes you claimed
4. Provides the final corrected rhyme scheme

Be concise and focus on the corrections.
```

**LLM Reflection**:
```
Thank you for the verification! I correctly identified both rhyme pairs:

✓ Lines 1-3 (πάει / φυσάει): Confirmed as PURE M rhyme
✓ Lines 2-4 (χορεύει / λαμπυρίζει): Confirmed as IMPERFECT F2 rhyme

Final Rhyme Scheme: ABAB
- A: M (Masculine) rhyme, PURE quality
- B: F2 (Paroxytone) rhyme, IMPERFECT quality (vowel differs: ε vs ι)

No corrections needed - all identified rhymes are phonologically valid.
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT: Greek Poem                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: LLM Initial Analysis                               │
│  ────────────────────────────────────                       │
│  • LLM reads poem                                           │
│  • Identifies rhyme pairs                                   │
│  • Outputs: "Lines 1 & 3 rhyme", etc.                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Symbolic Verification (Ground Truth)               │
│  ────────────────────────────────────────────               │
│  2a. Find ALL valid rhymes using phonological rules         │
│      • extract_rhyme_domain() for each line                 │
│      • classify_rhyme_pair() for all pairs                  │
│      • detect_stress_position() for M/F2/F3                 │
│                                                              │
│  2b. Parse LLM claims                                       │
│      • Extract line numbers from LLM output                 │
│      • Regex: "Lines 1 & 3" → (1, 3)                        │
│                                                              │
│  2c. Compare LLM vs Ground Truth                            │
│      • True Positives: LLM correct ✓                        │
│      • False Positives: LLM wrong ✗                         │
│      • False Negatives: LLM missed ✗                        │
│      • Calculate: Precision, Recall, F1                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: LLM Reflection & Correction                        │
│  ──────────────────────────────────────                     │
│  • Send verification results to LLM                         │
│  • LLM acknowledges correct identifications                 │
│  • LLM corrects mistakes                                    │
│  • LLM provides final corrected analysis                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: Combined Result                                    │
│  ────────────────────────────                               │
│  • Initial LLM analysis                                     │
│  • Verification metrics (Precision/Recall/F1)               │
│  • Detailed TP/FP/FN breakdown                              │
│  • LLM reflection & corrections                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Example: When LLM Makes Mistakes

### Input Poem
```
Στο δάσος περπατώ μονάχος
και βλέπω τα δεντράκια
που χορεύουν με τον ήλιο
και τραγουδούν τραγούδια
```

### Step 1: LLM Initial Analysis (with errors)
```
Rhyme Scheme: AABB
- Lines 1 & 2: μονάχος / δεντράκια (F3 rhyme)  ← WRONG!
- Lines 3 & 4: ήλιο / τραγούδια (F3 rhyme)     ← CORRECT
```

### Step 2: Symbolic Verification

**Ground Truth**:
```
Found 1 valid rhyme pair:
1. Lines 3-4: ήλιο / τραγούδια (PURE, F3)
```

**Comparison**:
```
GROUND TRUTH: 1 valid rhyme pair
LLM CLAIMED: 2 pairs

✓ TRUE POSITIVES: 1
  ✓ Lines 3-4: ήλιο / τραγούδια (PURE, F3)

✗ FALSE POSITIVES: 1
  ✗ Lines 1-2: μονάχος / δεντράκια - NOT a valid rhyme
  (Reason: Rhyme parts are 'axos' vs 'akja' - consonants don't match)

✗ FALSE NEGATIVES: 0

Precision: 50.0% (1 correct out of 2 claimed)
Recall: 100.0% (found all 1 valid rhymes)
F1 Score: 66.7%
```

### Step 3: LLM Reflection
```
Thank you for the correction. I made an error:

✓ Lines 3-4 (ήλιο / τραγούδια): Correctly identified as PURE F3 rhyme

✗ Lines 1-2 (μονάχος / δεντράκια): I incorrectly claimed this as a rhyme.
  The rhyme domains are:
  - μονάχος → 'axos' (stress on antepenult)
  - δεντράκια → 'akja' (stress on antepenult)
  
  While both are F3, the rhyme parts don't match phonetically:
  - 'axos' has /x/ (velar fricative)
  - 'akja' has /k/ (velar stop)
  These consonants differ in manner, so this is NOT a valid rhyme.

CORRECTED Rhyme Scheme: ABCB
- Only lines 3-4 rhyme (ήλιο / τραγούδια)
- Lines 1-2 do NOT rhyme
```

---

## Key Features

### 1. **No External Evaluators Needed**
- Uses your existing `greek_phonology.py` symbolic rules
- Ground truth is computed automatically
- No manual annotation required

### 2. **Precise Metrics**
- **Precision**: % of LLM claims that are correct
- **Recall**: % of actual rhymes that LLM found
- **F1 Score**: Harmonic mean of precision and recall

### 3. **Detailed Feedback**
- Shows exactly which rhymes LLM got right (TP)
- Shows exactly which rhymes LLM got wrong (FP)
- Shows exactly which rhymes LLM missed (FN)
- Includes rhyme types (PURE/RICH/IMPERFECT, M/F2/F3)

### 4. **LLM Learning**
- LLM sees its mistakes
- LLM provides corrected analysis
- Can improve over time with this feedback

---

## API Usage

### Endpoint: `/identify/verified`

**Request**:
```json
{
  "text": "Στη θάλασσα η καρδιά μου πάει\nκαι στα κύματα χορεύει...",
  "model": "gpt-4o",
  "prompt_strategy": "zero_shot_structured",
  "use_rag": true,
  "api_key": "your-api-key"
}
```

**Response**:
```json
{
  "result": "=== INITIAL LLM ANALYSIS ===\n...\n=== VERIFICATION ===\n...\n=== REFLECTION ===\n...",
  "llm_output": "Initial analysis...",
  "llm_reflection": "Corrected analysis...",
  "verification": {
    "ground_truth_rhymes": [...],
    "true_positives": [...],
    "false_positives": [...],
    "false_negatives": [...],
    "precision": 100.0,
    "recall": 100.0,
    "f1_score": 100.0,
    "verification_summary": "..."
  },
  "tokens_used": 1234
}
```

---

## Comparison: With vs Without Verification

### WITHOUT Verification (`/identify`)
```
Input: Poem
  ↓
LLM Analysis
  ↓
Output: LLM's rhyme identification
```
- **Fast**: 1 LLM call
- **No validation**: Could be wrong
- **No metrics**: Don't know accuracy

### WITH Verification (`/identify/verified`)
```
Input: Poem
  ↓
LLM Initial Analysis
  ↓
Symbolic Verification (Ground Truth)
  ↓
Compare LLM vs Ground Truth
  ↓
LLM Reflection & Correction
  ↓
Output: Initial + Verification + Corrected
```
- **Slower**: 2 LLM calls + symbolic analysis
- **Validated**: Know exactly what's right/wrong
- **Metrics**: Precision, Recall, F1
- **Educational**: LLM learns from mistakes

---

## Use Cases

### 1. **Evaluation**
Test LLM accuracy on known poems:
```python
# Test on corpus poems
for poem in corpus:
    result = await identify_rhymes_verified(poem)
    print(f"Precision: {result['verification']['precision']}")
    print(f"Recall: {result['verification']['recall']}")
```

### 2. **Quality Assurance**
Verify LLM output before showing to users:
```python
result = await identify_rhymes_verified(user_poem)
if result['verification']['f1_score'] < 80:
    # Show verification details to user
    return result['result']  # Includes corrections
else:
    # High confidence, show initial analysis
    return result['llm_output']
```

### 3. **Model Comparison**
Compare different models/prompts:
```python
models = ['gpt-4o', 'claude-sonnet-4.5', 'gemini-2.5-pro']
for model in models:
    result = await identify_rhymes_verified(poem, model=model)
    print(f"{model}: F1 = {result['verification']['f1_score']}")
```

### 4. **Training Data**
Generate corrected examples for fine-tuning:
```python
# Collect LLM mistakes and corrections
for poem in training_set:
    result = await identify_rhymes_verified(poem)
    if result['verification']['false_positives']:
        # Save as training example
        save_training_example(
            input=poem,
            wrong_output=result['llm_output'],
            correct_output=result['llm_reflection']
        )
```

---

## Summary

**Identification with Verification** = **LLM Analysis** + **Symbolic Validation** + **LLM Reflection**

- **Step 1**: LLM identifies rhymes
- **Step 2**: Symbolic rules verify (ground truth)
- **Step 3**: LLM reflects on mistakes

**Benefits**:
- ✅ Know exact accuracy (Precision/Recall/F1)
- ✅ Detailed error analysis (TP/FP/FN)
- ✅ LLM learns from mistakes
- ✅ No manual annotation needed

**Cost**:
- ⏱️ 2x LLM calls (slower)
- 💰 2x tokens (more expensive)

**When to use**:
- Evaluation and testing
- Quality assurance
- Model comparison
- When accuracy matters more than speed
