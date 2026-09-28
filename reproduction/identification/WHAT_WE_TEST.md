# EVALUATION SUMMARY - What We're Testing

## Quick Answer

We're testing **4 configurations** across **13 models** with **13 test cases**:

### 4 Configurations (2×2 matrix):
1. ✅ **WITH Verification + WITH RAG**
2. ✅ **WITH Verification + WITHOUT RAG**
3. ❌ **WITHOUT Verification + WITH RAG**
4. ❌ **WITHOUT Verification + WITHOUT RAG**

### 13 Models:
- Claude: `claude-sonnet-4.5`, `claude-sonnet-3.7`
- Gemini: `gemini-3-pro`, `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash`
- OpenAI: `gpt-4o`
- Open: `llama-3.3-70b`, `llama-3.1-70b`, `qwen-2.5-72b`, `mistral-large`

### 13 Test Cases:
All combinations of M/F2/F3 stress + PURE/RICH/IMPERFECT quality + MOSAIC/IDV features

---

## Total Tests

**Per Model**: 13 test cases × 4 configurations = **52 tests**
**All Models**: 52 × 13 models = **676 tests**

---

## What Each Test Measures

For each configuration, we measure:

### 1. Accuracy
- **Correct Pairs**: How many rhyme pairs satisfy ALL constraints
- **Total Pairs**: Total rhyme pairs in poem
- **Accuracy %**: (Correct / Total) × 100

### 2. Symbolic Validation
Each pair checked against:
- ✅ Rhyme exists (`classify_rhyme_pair`)
- ✅ Stress matches M/F2/F3 (`detect_stress_position`)
- ✅ Quality matches PURE/RICH/IMPERFECT
- ✅ MOSAIC if requested (`analyze_mosaic_pattern`)
- ✅ IDV if requested (`extract_pre_rhyme_vowel`)
- ✅ No identical words unless COPY requested

### 3. Performance
- **Time**: Generation time (seconds)
- **Attempts**: Iterations needed (verification mode only)

---

## Key Comparisons

### 1. Verification Impact
**Question**: Does the feedback loop help?

**Compare**: WITH vs WITHOUT verification (same RAG, same model, same test)

**Example**:
```
Config A: WITH Verification + WITH RAG
Config B: WITHOUT Verification + WITH RAG
→ Difference shows verification impact
```

### 2. RAG Impact
**Question**: Do corpus examples help?

**Compare**: WITH vs WITHOUT RAG (same verification, same model, same test)

**Example**:
```
Config A: WITH Verification + WITH RAG
Config C: WITH Verification + WITHOUT RAG
→ Difference shows RAG impact
```

### 3. Model Performance
**Question**: Which model is best?

**Compare**: All models (same configuration, same test)

**Example**:
```
GPT-4o vs Claude vs Gemini (all WITH Verification + WITH RAG)
→ Shows model rankings
```

### 4. Interaction Effects
**Question**: Does RAG help more when verification is disabled?

**Compare**: All 4 configurations

**Example**:
```
Config A: WITH Verification + WITH RAG      → 95% accuracy
Config B: WITH Verification + WITHOUT RAG   → 92% accuracy (RAG +3%)
Config C: WITHOUT Verification + WITH RAG   → 78% accuracy
Config D: WITHOUT Verification + WITHOUT RAG → 65% accuracy (RAG +13%)
→ RAG helps MORE when verification is disabled!
```

---

## Running Tests

### Quick Test (1 model, 3 cases, 4 configs = 12 tests)
```bash
python evaluate_system.py \
  --models gpt-4o \
  --test-cases quick_tests.json \
  --num-samples 1
```

### RAG-Only Test (skip no-RAG configs)
```bash
python evaluate_system.py \
  --models gpt-4o \
  --rag-only \
  --num-samples 1
```
This tests only 2 configurations: WITH/WITHOUT verification, both WITH RAG

### No-RAG Test (skip RAG configs)
```bash
python evaluate_system.py \
  --models gpt-4o \
  --no-rag \
  --num-samples 1
```
This tests only 2 configurations: WITH/WITHOUT verification, both WITHOUT RAG

### Full Test (all models, all configs)
```bash
python evaluate_system.py \
  --models all \
  --num-samples 1
```
This runs all 676 tests (13 models × 13 cases × 4 configs)

### Specific Models
```bash
python evaluate_system.py \
  --models claude-sonnet-4.5 gpt-4o gemini-2.5-pro \
  --num-samples 1
```
This runs 156 tests (3 models × 13 cases × 4 configs)

---

## Expected Results

### Verification Impact
- **Expected**: +20-30% accuracy improvement
- **Cost**: 3-5x slower
- **Most helpful for**: Complex features (MOSAIC, F3, RICH+IDV)

### RAG Impact
- **Expected**: +5-15% accuracy improvement
- **Cost**: Minimal (retrieval is fast)
- **Most helpful for**: Rare features (MOSAIC, IMPERFECT)
- **Interaction**: Helps MORE when verification is disabled

### Model Rankings (Predicted)
1. **Claude Sonnet 4.5**: Best overall, especially for complex Greek
2. **GPT-4o**: Fast and accurate, good balance
3. **Gemini 2.5 Pro**: Strong, especially with RAG
4. **Claude Sonnet 3.7**: Solid performance
5. **Gemini 2.5 Flash**: Fast, decent accuracy
6. **Llama 3.3 70B**: Best open model
7. **Qwen 2.5 72B**: Good for multilingual
8. **Mistral Large**: Decent performance
9. **Llama 3.1 70B**: Older, lower accuracy
10. **Gemini 2.0 Flash**: Fast but less accurate
11. **Gemini 2.5 Flash-Lite**: Fastest, lowest accuracy
12. **Gemini 3 Pro**: Experimental

### Feature Difficulty (Predicted)
1. **Hardest**: MOSAIC + RICH + IDV (complex combination)
2. **Hard**: F3 + IMPERFECT (rare in corpus)
3. **Medium**: MOSAIC alone, RICH + IDV
4. **Easy**: M + PURE, F2 + PURE
5. **Easiest**: M alone, F2 alone

---

## Output Analysis

After running, you'll get:

### Summary Statistics
```json
{
  "verification_impact": {
    "avg_accuracy_gain": 23.5,
    "avg_time_multiplier": 3.2
  },
  "rag_impact": {
    "avg_accuracy_gain": 8.7,
    "most_helpful_for": ["MOSAIC", "RICH"]
  },
  "model_rankings": [
    {"model": "claude-sonnet-4.5", "accuracy": 94.2},
    {"model": "gpt-4o", "accuracy": 91.8},
    ...
  ]
}
```

### Per-Model Breakdown
For each model, you'll see:
- Overall accuracy (all 52 tests)
- Accuracy by configuration (4 configs)
- Accuracy by test case (13 cases)
- Average time and attempts

### Per-Configuration Breakdown
For each of the 4 configs, you'll see:
- Overall accuracy (all 169 tests = 13 models × 13 cases)
- Best/worst models
- Best/worst test cases

---

## Research Questions Answered

1. **Should we always use verification?**
   - If accuracy gain > 20% and time cost < 5x → YES
   - If accuracy gain < 10% → Maybe not worth it

2. **Should we always use RAG?**
   - If accuracy gain > 5% → YES (minimal cost)
   - Check if it helps more for certain features

3. **Which model should we deploy?**
   - Best accuracy: Use top-ranked model
   - Best speed/accuracy: Find optimal tradeoff
   - Budget constraints: Use best open model

4. **Can we predict when verification is needed?**
   - If WITHOUT verification accuracy < 70% → Use verification
   - If test case is complex (MOSAIC, F3) → Use verification
   - If model is weak → Use verification

5. **Optimal production configuration?**
   - **High Quality**: Best model + Verification + RAG
   - **Balanced**: GPT-4o + Verification + RAG
   - **Fast**: Gemini Flash + No Verification + RAG
   - **Budget**: Llama 3.3 + Verification + RAG

---

## Next Steps

1. ✅ **Created**: Evaluation framework
2. ⏳ **Run**: Quick test to validate
3. ⏳ **Run**: Medium test (3 models)
4. ⏳ **Analyze**: Initial findings
5. ⏳ **Run**: Full test (all models)
6. ⏳ **Publish**: Results and recommendations
