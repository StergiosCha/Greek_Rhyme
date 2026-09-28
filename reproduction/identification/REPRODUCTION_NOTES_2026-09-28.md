# Greek_Rhyme: πού βρίσκονται τα υλικά του rhyme identification evaluation (Πίνακες 2 και 3)

Σημειώσεις για την αναπαραγωγή, με βάση τον φάκελο εργασίας `~/Dropbox/greek_rhyme_System_verified/` (όλα τα paths παρακάτω είναι σχετικά ως προς αυτόν, εκτός αν λέγεται αλλιώς). Ημερομηνία ελέγχου: 28/9/2026.

## 1. Το test set και οι ετικέτες

Υπάρχουν δύο σύνολα, και τα δύο με ενσωματωμένες τις αναμενόμενες ετικέτες (`rhyme_type`, `features`, `pattern`):

| Αρχείο | Ποιήματα (ζεύγη στίχων) | Κατανομή | Δημιουργήθηκε |
|---|---|---|---|
| `golden_test_set.json` | 26 | 8 M, 10 F2, 8 F3 | 10/12/2025, `create_golden_set.py` (εξάγει τα `test_poems` από το `identification_checkpoint_claude_sonnet_3.7.json`, τα οποία είχαν δειγματοληφθεί τυχαία, χωρίς seed, από το `complete_corpus_enhanced.json` της εποχής) |
| `complementary_test_set.json` | 14 | 5 M, 6 F2, 3 F3 | 10/12/2025, `create_complementary_set.py` (τυχαία δειγματοληψία, χωρίς seed, με στόχο σπάνιους τύπους: MOSAIC, IMPERFECT, F3-PURE) |

Άθροισμα: 40 ποιήματα, 13 M / 16 F2 / 11 F3. Αυτό ακριβώς είναι το «40 poems, 160 test cases» του Experimental Setup στο paper.

Το βασικό εύρημα: **οι Πίνακες 2 και 3 του paper υπολογίστηκαν μόνο πάνω στα 26 του golden set** (104 tests ανά μοντέλο = 26 × 2 strategies × 2 RAG). Το επιβεβαιώνουν δύο πράγματα: (α) όλες οι τιμές του Πίνακα 2 είναι πολλαπλάσια του 1/26 (3.85%), και (β) τα n του Πίνακα 3 (M=32, F2=40, F3=32) είναι 8×4, 10×4, 8×4. Επανυπολόγισα τους πίνακες από τα αποθηκευμένα αρχεία και ταυτίζονται στο δέκατο. Τα 14 complementary τρέξανε για όλα τα μοντέλα (`complementary_results_*.json`) αλλά δεν συγχωνεύτηκαν στους πίνακες. Δηλαδή το κείμενο του Experimental Setup περιγράφει την ένωση των δύο συνόλων, ενώ οι πίνακες αναφέρονται μόνο στο πρώτο. Στην ενότητα 5 δίνω τα νούμερα και για τα 40.

Το `evaluate_identification.py` του GitHub repo (default `num_samples=26`) δεν είναι το script που έδωσε τα αποτελέσματα. Δειγματοληπτεί εκ νέου τυχαία 26 ζεύγη από το corpus, χωρίς seed, οπότε δεν μπορεί να αναπαραγάγει το ίδιο σύνολο. Το script που τρέχει το golden set είναι το `run_identification_single.py` (φορτώνει το `golden_test_set.json` αν υπάρχει), και για τα complementary το `run_complementary_identification.py`.

## 2. Προέλευση των ετικετών (human verification ή verifier;)

Οι ετικέτες προέρχονται αποκλειστικά από τον phonological verifier. Συγκεκριμένα, είναι το πεδίο `classification` της αντίστοιχης εγγραφής του corpus, όπως το παράγει το `greek_phonology.py` (κανόνες κατά Topintzi 2019), και το `pattern` του test set είναι κατά λέξη αυτό το string (π.χ. `F3-IMP-C-IMPERFECT-IDV`). Δεν υπάρχει βήμα ανθρώπινου ελέγχου: το `create_golden_set.py` απλώς εξάγει τα ποιήματα από ένα checkpoint, και το `create_complementary_set.py` δειγματοληπτεί από το corpus. Το «verified» στα READMEs σημαίνει ότι το corpus είχε περάσει από τον αυτόματο καθαρισμό `clean_dataset.py` (regex για λατινικούς χαρακτήρες, αριθμούς, σύμβολα, αφαίρεση `UNKNOWN`), όχι ότι κάποιος έλεγξε τα 40 ζεύγη.

Ενδείξεις ότι χρειάζεται ανθρώπινος έλεγχος πριν από οποιοδήποτε μεγαλύτερο gold benchmark:

* Στο golden set υπάρχει η εγγραφή `[Ο επίλογος] / Ο επίλογος` με ετικέτα `F3-RICH-IDV`: είναι τίτλος που επαναλαμβάνεται, όχι ομοιοκαταληξία. Επίσης `Τσαρλατάνος; * α! δε γένουμαι.` (με αστερίσκο OCR).
* Ένα από τα 40 ζεύγη («Κι εσύ, ξέστηθη δούλα, στο πηγάδι γειρτή...») έχει ετικέτα `M-MOSAIC` στο test set αλλά `M-PURE` στο σημερινό `complete_corpus_enhanced.json` (rebuild 26/12/2025). Δηλαδή οι ετικέτες αλλάζουν με την έκδοση του verifier.
* Υπάρχουν δύο ορθογραφίες του ίδιου feature (`IMP` και `IMPERFECT`) και βοηθητικά flags (`V`, `C`) μέσα στο `features`, που μετράνε στο feature F1 και κατεβάζουν τεχνητά τα σκορ των features.
* Τα feature counts του Experimental Setup (21 PURE, 10 RICH, 10 IDV, 6 IMPERFECT, 5 MOSAIC) δεν συμφωνούν ακριβώς με το άθροισμα των δύο αρχείων (22 PURE, 7 RICH, 8 IDV, 6 IMPERFECT, 5 MOSAIC). Τα rhyme-type counts (13/16/11) συμφωνούν.

## 3. Έκδοση κώδικα και ρυθμίσεις

* Πυρήνας: `greek_phonology.py`, `prompts.py`, `verification_utils.py`. Τα τοπικά αντίγραφα είναι byte-identical (ίδιο md5) με τα `src/` του GitHub repo (commit `03043b5`, 26/12/2025) και με το `GreekRhyme_Reproduction/src/`. Το OSF archive (`https://osf.io/d7hr6/`, Archive.zip) περιέχει ακριβώς το περιεχόμενο του GitHub repo. Επιφύλαξη: το `prompts.py` έχει mtime 23/12/2025, δύο εβδομάδες μετά τα runs (10/12/2025), και τα results δεν αποθηκεύουν το prompt, μόνο το `raw_output`. Οπότε η ταύτιση prompt-κώδικα με τα runs είναι πολύ πιθανή αλλά όχι αποδείξιμη.
* Scripts εκτέλεσης: `run_identification_single.py <model>` (golden) και `run_complementary_identification.py <model>` (complementary). Δεν υπάρχουν στο δημόσιο repo. Καλούν το `call_model()` του `app.py`.
* Κλήσεις μοντέλων (`app.py`, `call_model`): `max_tokens=4000` για Anthropic και OpenAI, χωρίς ρύθμιση `temperature` (default του κάθε provider), ένα request ανά test, χωρίς retries στα results (τα errors γράφονται ως `raw_output`).
* Strategies: `zero_shot_structured`, `zero_shot_cot` (`prompts.py`, `get_identification_prompt`). RAG: 15 παραδείγματα, `random.sample` χωρίς seed, από τα πρώτα 50 entries κάθε ποιητή, εξαιρώντας το ίδιο το test ζεύγος. Άρα τα +RAG runs δεν είναι bit-for-bit αναπαραγώγιμα.
* Model IDs (από το `app.py` του repo, ίδιο mapping από το πρώτο commit 19/11/2025 ως το 26/12/2025, και από το τοπικό `app_patched.py`):
  * `claude-sonnet-3.7` → `claude-3-7-sonnet-20250219`
  * `claude-sonnet-4.5` → **`claude-sonnet-4-20250514`** (δηλαδή Claude Sonnet 4, όχι Sonnet 4.5). Αυτό πρέπει να ελεγχθεί και μάλλον να διορθωθεί στο paper: ό,τι λέγεται «Claude 4.5» στους πίνακες πιθανότατα είναι Sonnet 4.
  * `gpt-4o` → `gpt-4o` (alias, χωρίς ημερομηνία)
  * `gemini-2.0-flash` → `gemini-2.0-flash-exp`
  * OpenRouter: `meta-llama/llama-3.1-70b-instruct`, `meta-llama/llama-3.3-70b-instruct`, `meta-llama/llama-3.1-8b-instruct`, `mistralai/mistral-large`
* Περιβάλλον: Python 3.12.8 (`venv/pyvenv.cfg`), `requirements_full.txt`.
* Corpus την ώρα των runs: το `complete_corpus_enhanced.json` της 10/12/2025 (πολλαπλοί ποιητές). Το σημερινό αρχείο με το ίδιο όνομα είναι rebuild της 26/12/2025 και έχει άλλη δομή (μόνο Anemoskala, 33.018 entries). Το πλησιέστερο snapshot είναι το `complete_corpus_enhanced_BACKUP_20251210_153502.json`. Για τα Tables 2 και 3 δεν χρειάζεται το corpus: οι ετικέτες είναι μέσα στα test sets, το corpus χρειάζεται μόνο για το RAG context.

## 4. Αρχικά outputs και scoring

Ανά μοντέλο, με `raw_output` (πλήρης απάντηση LLM), `predicted_*`, `true_*`, `rhyme_type_correct`, `features_precision/recall/f1`, `time_taken`:

| Μοντέλο | Golden (104 tests) | Complementary (56 tests) |
|---|---|---|
| Claude «4.5» | `identification_results_claude_sonnet_4.5.json` | `complementary_results_claude_sonnet_4.5.json` |
| Claude 3.7 | `identification_results_claude_sonnet_3.7_FIXED.json` (το χωρίς `_FIXED` έχει 0% παντού λόγω bug στον parser και έγινε ξανά parse με τη λογική του `fix_results.py`) | `complementary_results_claude_sonnet_3.7.json` |
| GPT-4o | `identification_results_gpt_4o.json` | `complementary_results_gpt_4o.json` |
| Gemini 2.0 | `identification_results_gemini_2.0_flash.json` | `complementary_results_gemini_2.0_flash.json` |
| Mistral Large | `identification_results_mistral_large.json` | `complementary_results_mistral_large.json` |
| Llama 3.1 70B | `identification_results_llama_3.1_70b.json` | `complementary_results_llama_3.1_70b.json` |
| Llama 3.3 70B | `identification_results_llama_3.3_70b.json` | `complementary_results_llama_3.3_70b.json` |
| Llama 3.1 8B | `identification_results_llama_3.1_8b.json` | `complementary_results_llama_3.1_8b.json` |

Αντίστοιχα `identification_checkpoint_*.json` / `complementary_checkpoint_*.json` (περιέχουν και τα `test_poems`, ταυτόσημα με τα test sets) και logs `ident_*.log`, `complementary_*_log.txt`. Τα `*_DIRTY.json` είναι runs πάνω στο μη καθαρισμένο corpus πριν τις 10/12 και δεν χρησιμοποιούνται. Το `identification_results_claude_sonnet_4.5_FIXED.json` δεν χρησιμοποιήθηκε στους πίνακες (ο Πίνακας 2 ταιριάζει με το χωρίς `_FIXED`).

Scoring: rhyme type = exact match `predicted_rhyme_type == true_rhyme_type`, features = set P/R/F1 (κώδικας μέσα στο `run_identification_single.py`, `run_single_test`). Parsing του LLM output: `verification_utils.parse_llm_rhyme_output`. Scripts παραγωγής πινάκων: `show_all_ident_results.py` (Πίνακας 2), `generate_rhyme_type_table.py` (Πίνακας 3), `generate_feature_table.py` (Appendix). Συνοπτικά έγγραφα: `IDENTIFICATION_RESULTS_SUMMARY.md`, `EVALUATION_STATISTICS.txt`, `IDENTIFICATION_VERIFICATION_EXPLAINED.md`, `WHAT_WE_TEST.md`.

Προσοχή πριν δοθεί ο φάκελος: τα `run_identification_single.py`, `run_complementary_identification.py` και `evaluate_identification.py` (τοπικές εκδόσεις) έχουν hard-coded API keys (Anthropic, OpenAI, Google, OpenRouter). Στο GitHub και στο OSF δεν υπάρχουν keys (ελέγχθηκε και το git history). Τα keys πρέπει να αφαιρεθούν πριν από κάθε κοινοποίηση, και καλό είναι να ανακληθούν.

## 5. Πίνακες 2 και 3 ξαναϋπολογισμένοι και στα 40 ποιήματα (160 tests ανά μοντέλο)

Rhyme-type accuracy ανά configuration (Structured / Structured+RAG / CoT / CoT+RAG) και ανά τύπο (M n=52, F2 n=64, F3 n=44):

| Μοντέλο | Struct | S+RAG | CoT | CoT+RAG | M | F2 | F3 |
|---|---|---|---|---|---|---|---|
| Claude «4.5» (sonnet-4-20250514) | 50.0 | 22.5 | 57.5 | 52.5 | 65.4 | 43.8 | 25.0 |
| Claude 3.7 | 47.5 | 47.5 | 42.5 | 40.0 | 38.5 | 51.6 | 40.9 |
| GPT-4o | 5.0 | 10.0 | 45.0 | 32.5 | 25.0 | 23.4 | 20.5 |
| Gemini 2.0 | 17.5 | 40.0 | 15.0 | 17.5 | 38.5 | 17.2 | 11.4 |
| Mistral Large | 10.0 | 22.5 | 32.5 | 17.5 | 26.9 | 20.3 | 13.6 |
| Llama 3.1 70B | 15.0 | 20.0 | 17.5 | 12.5 | 11.5 | 28.1 | 4.5 |
| Llama 3.3 70B | 27.5 | 32.5 | 15.0 | 7.5 | 26.9 | 21.9 | 11.4 |
| Llama 3.1 8B | 12.5 | 12.5 | 5.0 | 5.0 | 9.6 | 10.9 | 4.5 |

Η γενική εικόνα (Claude κορυφή, GPT-4o κερδίζει πολύ από CoT, F3 το δυσκολότερο, ανοιχτά μοντέλα χαμηλά) διατηρείται. Αλλάζουν επιμέρους σημεία: το καλύτερο config του Claude «4.5» γίνεται σκέτο CoT (57.5%) αντί CoT+RAG, ο Claude 3.7 ανεβαίνει στο F3 (40.9%), και η κατάταξη Struct vs CoT στα Llama αλλάζει.

## 6. Τι δεν υπάρχει και θα χρειαστεί για την επέκταση

* Δεν υπάρχει seed πουθενά (δειγματοληψία test set, RAG examples). Τα σύνολα είναι πλέον fixed στα δύο JSON, αλλά το RAG context δεν αναπαράγεται ακριβώς.
* Δεν υπάρχει καταγραφή του ακριβούς prompt ανά test (μόνο `raw_output`).
* Δεν υπάρχει ανθρώπινη επικύρωση των ετικετών, ούτε inter-annotator agreement.
* Το δημόσιο repo δεν περιέχει τα test sets, τα results, ούτε το script που τρέχει το golden set. Για να είναι αναπαραγώγιμο το paper, χρειάζεται να ανέβουν: `golden_test_set.json`, `complementary_test_set.json`, `run_identification_single.py` και `run_complementary_identification.py` (χωρίς keys), τα `identification_results_*.json` / `complementary_results_*.json`, και τα scripts των πινάκων.
