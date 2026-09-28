# Reproduction materials

Everything needed to re-score the tables in

> Chatzikyriakidis, S. and Natsina, A. (2026). *LLMs Got Rhyme? Hybrid Phonological Filtering for Greek Poetry Rhyme Detection and Generation.* LaTeCH-CLfL 2026. https://aclanthology.org/2026.latechclfl-1.9/

without calling any model API, plus the scripts that produced the raw outputs in December 2025. The paper's Tables 2 and 3 (identification) and Table 5 (generation) can be regenerated from the files here with the commands below.

The core modules (`greek_phonology.py`, `prompts.py`, `verification_utils.py`) are the ones in `../src/`; the copies used for the runs are byte-identical to them.

## Layout

```
reproduction/
  identification/
    golden_test_set.json            26 rhyme pairs with labels (8 M, 10 F2, 8 F3)
    complementary_test_set.json     14 rhyme pairs with labels (5 M, 6 F2, 3 F3), rare types
    results/                        per-item scored outputs, one file per model and set
    checkpoints/                    same content plus the test_poems list, written during the runs
    logs/                           console logs of the runs
    scripts/                        run, scoring and table scripts (see below)
    REPRODUCTION_NOTES_2026-09-28.md  detailed provenance notes (in Greek)
    IDENTIFICATION_RESULTS_SUMMARY.md, EVALUATION_STATISTICS.txt, ...  working notes from the runs
  generation/
    checkpoint_<model>.json         generation results (26 constrained prompts, with/without verifier)
    analyze_evaluation_results.py   scoring of the generation checkpoints
    test_all_models.py              driver used for the generation runs
    EVALUATION_26_RESULTS.md, EVALUATION_README.md, EVALUATION_TEST_MATRIX.md
```

## Which set the tables use

The paper's Experimental Setup describes a test set of 40 pairs (13 M, 16 F2, 11 F3). That is the union of `golden_test_set.json` (26) and `complementary_test_set.json` (14). **Tables 2 and 3 as published were computed on the 26-pair golden set only** (104 tests per model: 26 pairs x 2 strategies x 2 RAG settings). This is why every value in Table 2 is a multiple of 1/26 and the n values in Table 3 are 32/40/32. The complementary set was run for all eight models (`results/complementary_results_*.json`) but was not merged into the published tables. `REPRODUCTION_NOTES_2026-09-28.md` gives both tables recomputed on all 40 pairs.

Labels (`rhyme_type`, `features`, `pattern`) are the corpus `classification` strings produced by the phonological engine (`src/greek_phonology.py`), following the Topintzi (2019) taxonomy. They were not manually verified. Feature strings contain both `IMP` and `IMPERFECT`, and the flags `V` and `C`; all of these count in the feature F1.

## Re-scoring the published tables (no API calls)

```bash
cd reproduction/identification/results

# Table 2: accuracy per model and configuration
python ../scripts/show_all_ident_results.py

# Table 3: accuracy by rhyme type
python ../scripts/generate_rhyme_type_table.py

# Appendix feature-F1 table
python ../scripts/generate_feature_table.py

# Per-file breakdown
python ../scripts/analyze_ident.py identification_results_claude_sonnet_4.5.json
```

The table scripts read the result files by name from the current directory. For Claude 3.7 the file used is `identification_results_claude_sonnet_3.7_FIXED.json`; the non-`FIXED` file was written with a parser bug (0% everywhere) and was re-parsed with the logic in `scripts/fix_results.py`. `identification_results_claude_sonnet_4.5_FIXED.json` and the `*_DIRTY*` checkpoints were not used.

Generation (Table 5) is the first 26 entries of each `generation/checkpoint_<model>.json`:

```bash
cd reproduction/generation
python analyze_evaluation_results.py
```

Some generation checkpoints contain more than 26 entries (re-runs appended) or fewer (aborted runs: Gemini 2.5 Flash, Llama 3.3 70B, Qwen 2.5 72B); the paper reports Claude 3.7, Claude "4.5" and GPT-4o on the first 26.

## Re-running the models

Set the keys as environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`), then from the repository root with `PYTHONPATH` including `src` and the run scripts placed next to `app.py`:

```bash
python reproduction/identification/scripts/run_identification_single.py claude-sonnet-3.7
python reproduction/identification/scripts/run_complementary_identification.py claude-sonnet-3.7
```

`run_identification_single.py` loads `golden_test_set.json` if present in the working directory, otherwise it samples 26 pairs from the corpus. `src/evaluate_identification.py` is an earlier driver that always resamples; it does not reproduce the published test set.

Settings at run time (`app.py`, `call_model`): `max_tokens=4000` for Anthropic and OpenAI, no explicit temperature (provider defaults), one request per test. RAG prompts draw 15 examples with an unseeded `random.sample`, so RAG runs are not bit-for-bit reproducible. Strategies: `zero_shot_structured`, `zero_shot_cot` (`src/prompts.py`, `get_identification_prompt`).

Model identifiers used (from `app.py` at the time of the runs; `scripts/app_patched.py` keeps the December 2025 mapping):

| Paper label | API model |
|---|---|
| Claude 3.7 | `claude-3-7-sonnet-20250219` |
| Claude 4.5 | `claude-sonnet-4-20250514` (see note) |
| GPT-4o | `gpt-4o` |
| Gemini 2.0 | `gemini-2.0-flash-exp` |
| Llama 3.1 70B / 3.3 70B / 3.1 8B | `meta-llama/llama-3.1-70b-instruct`, `meta-llama/llama-3.3-70b-instruct`, `meta-llama/llama-3.1-8b-instruct` (OpenRouter) |
| Mistral Large | `mistralai/mistral-large` (OpenRouter) |

**Note on "Claude 4.5":** the configuration key `claude-sonnet-4.5` was mapped to the API model `claude-sonnet-4-20250514`, i.e. Claude Sonnet 4, in every version of `app.py` from the first commit through the runs. The rows labelled "Claude 4.5" in the paper should therefore be read as Claude Sonnet 4. A corrigendum is being prepared.

The corpus file used for RAG context during the December 10, 2025 runs was the multi-poet `complete_corpus_enhanced.json` of that date; `data/complete_corpus_enhanced.json` in this repository is the December 26 rebuild (Anemoskala only, different structure). The test-set files carry their own labels, so the corpus is only needed for the RAG condition.

## Result file format

Each entry in `results/*.json`:

```
test_id, model, strategy, use_rag, poem_text, poet,
true_rhyme_type, true_features,
predicted_rhyme_type, predicted_features,
rhyme_type_correct, features_correct, features_precision, features_recall, features_f1,
time_taken, raw_output
```

`raw_output` is the full model response. Rhyme-type accuracy is exact match; feature scores are set precision/recall/F1 over the feature list. Parsing of model output: `src/verification_utils.py`, `parse_llm_rhyme_output`.
