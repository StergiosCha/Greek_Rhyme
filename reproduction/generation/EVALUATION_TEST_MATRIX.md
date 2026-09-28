# Evaluation Test Matrix

## What We're Testing

This evaluation framework tests the Greek Rhyme System across **multiple dimensions** to understand:
1. **Impact of Verification**: Does the feedback loop improve accuracy?
2. **Impact of RAG**: Do retrieval-augmented examples help?
3. **Model Performance**: Which models perform best?
4. **Parameter Combinations**: Which rhyme types and features are hardest?

---

## Test Dimensions

### 1. **Verification Mode** (2 variants)
- ✅ **WITH Verification**: Uses feedback loop (up to 15 attempts)
- ❌ **WITHOUT Verification**: Single-shot generation (fast)

### 2. **RAG Mode** (2 variants)
- ✅ **WITH RAG**: Retrieves examples from corpus
- ❌ **WITHOUT RAG**: No examples, pure LLM generation

### 3. **Models** (13 models)
From `app.py` MODEL_CONFIGS:

**Claude Models:**
- `claude-sonnet-4.5` (Anthropic)
- `claude-sonnet-3.7` (Anthropic)

**Gemini Models:**
- `gemini-3-pro` (Google)
- `gemini-2.5-pro` (Google)
- `gemini-2.5-flash` (Google)
- `gemini-2.5-flash-lite` (Google)
- `gemini-2.0-flash` (Google)

**OpenAI:**
- `gpt-4o` (OpenAI)

**Open Models (via OpenRouter):**
- `llama-3.3-70b` (Meta)
- `llama-3.1-70b` (Meta)
- `qwen-2.5-72b` (Qwen)
- `mistral-large` (Mistral)

### 4. **Rhyme Types** (3 types)
- **M** (Masculine/Oxytone): Stress on final syllable
- **F2** (Paroxytone): Stress on penultimate syllable
- **F3** (Proparoxytone): Stress on antepenultimate syllable

### 5. **Rhyme Quality** (3 types)
- **PURE**: Perfect sound match from stressed vowel
- **RICH**: Onset of stressed syllable also matches
- **IMPERFECT**: Partial match (vowel or consonant differs)

### 6. **Special Features** (3 features)
- **MOSAIC**: Rhyme spans word boundaries
- **IDV**: Pre-stress vowels match
- **COPY**: Identical words (usually rejected unless requested)

---

## Complete Test Matrix

### Total Combinations
- **Verification**: 2 (with/without)
- **RAG**: 2 (with/without)
- **Models**: 13
- **Test Cases**: 13 (from DEFAULT_TEST_CASES)

**Total Tests per Model**: 13 test cases × 2 RAG modes × 2 verification modes = **52 tests**
**Total Tests Overall**: 52 × 13 models = **676 tests**

### Test Cases (13 scenarios)

```python
DEFAULT_TEST_CASES = [
    # 1-3: Basic stress types (no features)
    {'theme': 'αγάπη', 'rhyme_type': 'M', 'features': []},
    {'theme': 'θάλασσα', 'rhyme_type': 'F2', 'features': []},
    {'theme': 'ουρανός', 'rhyme_type': 'F3', 'features': []},
    
    # 4-6: Rhyme quality types
    {'theme': 'φως', 'rhyme_type': 'M', 'features': ['PURE']},
    {'theme': 'νύχτα', 'rhyme_type': 'F2', 'features': ['RICH']},
    {'theme': 'ελπίδα', 'rhyme_type': 'F3', 'features': ['IMPERFECT']},
    
    # 7-9: Combined features (stress + quality + IDV)
    {'theme': 'καρδιά', 'rhyme_type': 'M', 'features': ['PURE', 'IDV']},
    {'theme': 'όνειρο', 'rhyme_type': 'F2', 'features': ['RICH', 'IDV']},
    {'theme': 'μνήμη', 'rhyme_type': 'F3', 'features': ['IMPERFECT', 'IDV']},
    
    # 10-11: Mosaic rhymes
    {'theme': 'φεγγάρι', 'rhyme_type': 'M', 'features': ['MOSAIC']},
    {'theme': 'άνεμος', 'rhyme_type': 'F2', 'features': ['MOSAIC']},
    
    # 12-13: Complex combinations
    {'theme': 'χρόνος', 'rhyme_type': 'M', 'features': ['RICH', 'MOSAIC']},
    {'theme': 'ψυχή', 'rhyme_type': 'F2', 'features': ['PURE', 'IDV', 'MOSAIC']},
]
```

---

## What Each Test Measures

### For Each Configuration (Verification × RAG × Model × Test Case):

#### 1. **Accuracy Metrics**
- **Correct Pairs**: Number of rhyme pairs that satisfy ALL constraints
- **Total Pairs**: Total rhyme pairs in the poem
- **Accuracy %**: (Correct / Total) × 100
- **Valid**: Boolean - are ALL pairs correct?

#### 2. **Constraint Validation** (Symbolic Rules)
For each rhyme pair, we check:
- ✅ **Rhyme Exists**: `classify_rhyme_pair()` returns non-NONE
- ✅ **Stress Match**: `detect_stress_position()` matches M/F2/F3
- ✅ **Quality Match**: PURE/RICH/IMPERFECT matches request
- ✅ **MOSAIC**: `analyze_mosaic_pattern()` confirms word boundaries
- ✅ **IDV**: `extract_pre_rhyme_vowel()` confirms vowel match
- ✅ **No COPY**: Words aren't identical (unless requested)

#### 3. **Performance Metrics**
- **Time**: Generation time in seconds
- **Attempts**: Number of iterations (for verification mode)
- **Tokens**: LLM tokens used (if available)

#### 4. **Error Analysis**
- **Error Types**: Categorized by which constraint failed
- **Error Rate**: Percentage of pairs with each error type

---

## Comparison Dimensions

### 1. **Verification Impact**
**Question**: Does verification improve accuracy?

**Comparison**:
```
WITH Verification vs WITHOUT Verification
(same RAG mode, same model, same test case)
```

**Expected**: WITH should have higher accuracy but take longer

**Metrics**:
- Accuracy gain (percentage points)
- Time cost (multiplier)
- Attempt count

### 2. **RAG Impact**
**Question**: Do corpus examples help?

**Comparison**:
```
WITH RAG vs WITHOUT RAG
(same verification mode, same model, same test case)
```

**Expected**: WITH RAG should provide better examples, especially for complex features

**Metrics**:
- Accuracy gain
- Quality of rhymes (PURE vs IMPERFECT)
- Feature adherence (MOSAIC, IDV success rate)

### 3. **Model Performance**
**Question**: Which models are best for Greek rhyme generation?

**Comparison**:
```
Model A vs Model B vs Model C...
(same verification mode, same RAG mode, same test case)
```

**Expected**: Larger models (Claude, GPT-4o) should outperform smaller ones

**Metrics**:
- Overall accuracy across all test cases
- Success rate per rhyme type (M/F2/F3)
- Success rate per feature (PURE/RICH/IMPERFECT/MOSAIC/IDV)
- Speed

### 4. **Feature Difficulty**
**Question**: Which rhyme types/features are hardest?

**Comparison**:
```
Test Case 1 vs Test Case 2 vs Test Case 3...
(across all models and configurations)
```

**Expected**: Complex features (MOSAIC, F3, RICH+IDV) should be harder

**Metrics**:
- Average accuracy per test case
- Failure rate per constraint type
- Attempts needed (for verification mode)

---

## Output Structure

### Summary Statistics
```json
{
  "overall": {
    "total_tests": 676,
    "models_tested": 13,
    "test_cases": 13,
    "configurations": 4  // (verification × RAG)
  },
  
  "verification_impact": {
    "avg_accuracy_gain": 23.5,  // percentage points
    "avg_time_multiplier": 3.2,
    "success_rate_improvement": 15.0  // percentage points
  },
  
  "rag_impact": {
    "avg_accuracy_gain": 8.7,
    "most_helpful_for": ["MOSAIC", "RICH"],
    "least_helpful_for": ["M", "PURE"]
  },
  
  "model_rankings": [
    {"model": "claude-sonnet-4.5", "accuracy": 94.2, "avg_time": 5.3},
    {"model": "gpt-4o", "accuracy": 91.8, "avg_time": 4.1},
    ...
  ],
  
  "feature_difficulty": [
    {"feature": "MOSAIC", "avg_accuracy": 67.3, "avg_attempts": 4.2},
    {"feature": "F3", "avg_accuracy": 72.1, "avg_attempts": 3.8},
    ...
  ]
}
```

### Detailed Results
```json
{
  "results": [
    {
      "test_id": "claude-sonnet-4.5_rag-yes_verify-yes_case-1",
      "model": "claude-sonnet-4.5",
      "use_rag": true,
      "use_verification": true,
      "test_case": {...},
      "accuracy": 100.0,
      "time": 8.3,
      "attempts": 2,
      "errors": []
    },
    ...
  ]
}
```

---

## Recommended Test Runs

### Quick Test (Development)
- **Models**: 1 (e.g., `gpt-4o`)
- **Test Cases**: 3 (basic M, F2, F3)
- **Configurations**: 4 (all RAG × verification combos)
- **Total**: 12 tests (~5 minutes)

```bash
python evaluate_system.py \
  --models gpt-4o \
  --test-cases quick_tests.json \
  --num-samples 1
```

### Medium Test (Validation)
- **Models**: 3 (e.g., Claude, GPT-4o, Gemini)
- **Test Cases**: 13 (all)
- **Configurations**: 4
- **Total**: 156 tests (~1 hour)

```bash
python evaluate_system.py \
  --models claude-sonnet-4.5 gpt-4o gemini-2.5-pro \
  --num-samples 1
```

### Full Test (Research)
- **Models**: 13 (all)
- **Test Cases**: 13 (all)
- **Configurations**: 4
- **Total**: 676 tests (~4-6 hours)

```bash
python evaluate_system.py \
  --models all \
  --num-samples 1
```

### Statistical Test (Publication)
- **Models**: 13 (all)
- **Test Cases**: 13 (all)
- **Configurations**: 4
- **Samples**: 3 (for statistical significance)
- **Total**: 2,028 tests (~12-18 hours)

```bash
python evaluate_system.py \
  --models all \
  --num-samples 3
```

---

## Analysis Questions

After running the evaluation, we can answer:

1. **Is verification worth it?**
   - How much does accuracy improve?
   - What's the time cost?
   - For which features is it most valuable?

2. **Does RAG help?**
   - Overall accuracy improvement?
   - Which features benefit most?
   - Does it reduce attempts needed?

3. **Which model is best?**
   - Overall accuracy ranking
   - Speed vs accuracy tradeoff
   - Which models handle complex features best?

4. **Which features are hardest?**
   - Failure rates by feature
   - Which combinations are most challenging?
   - Do models struggle with specific constraints?

5. **Optimal configuration?**
   - Best model for production
   - Should we always use RAG?
   - Should we always use verification?
   - Can we predict when verification is needed?

---

## Next Steps

1. **Run Quick Test**: Validate the evaluation framework works
2. **Run Medium Test**: Get initial insights on model performance
3. **Analyze Results**: Identify patterns and optimal configurations
4. **Run Full Test**: Comprehensive evaluation for all models
5. **Statistical Analysis**: Multiple samples for significance testing
6. **Publish Results**: Document findings and recommendations
