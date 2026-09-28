import json
import statistics

models = {
    'Claude 4.5': 'identification_results_claude_sonnet_4.5.json',
    'Claude 3.7': 'identification_results_claude_sonnet_3.7_FIXED.json',
    'GPT-4o': 'identification_results_gpt_4o.json',
    'Gemini 2.0': 'identification_results_gemini_2.0_flash.json',
    'Llama 3.1': 'identification_results_llama_3.1_70b.json',
    'Llama 3.3': 'identification_results_llama_3.3_70b.json',
    'Mistral': 'identification_results_mistral_large.json',
    'Llama 3.1 8B': 'identification_results_llama_3.1_8b.json'
}

print("="*80)
print("FEATURE DETECTION F1 SCORES")
print("="*80)
print(f"{'Model':<15} {'Overall F1':<12} {'Best Config':<20} {'Best F1':<10}")
print("-"*80)

for model_name, filename in models.items():
    try:
        with open(filename) as f:
            results = json.load(f)
        
        # Overall F1
        overall_f1 = statistics.mean(r['features_f1'] for r in results)
        
        # By config
        by_config = {}
        for r in results:
            key = (r['strategy'], r['use_rag'])
            if key not in by_config:
                by_config[key] = []
            by_config[key].append(r['features_f1'])
        
        best_config = max(by_config.items(), key=lambda x: statistics.mean(x[1]))
        config_name = f"{best_config[0][0].replace('zero_shot_', '')} {'+ RAG' if best_config[0][1] else ''}"
        best_f1 = statistics.mean(best_config[1])
        
        print(f"{model_name:<15} {overall_f1:>6.3f}      {config_name:<20} {best_f1:>6.3f}")
    except FileNotFoundError:
        print(f"{model_name:<15} NOT FOUND")

print("\n" + "="*80)
print("LATEX TABLE FORMAT")
print("="*80)

for model_name, filename in models.items():
    try:
        with open(filename) as f:
            results = json.load(f)
        
        overall_f1 = statistics.mean(r['features_f1'] for r in results)
        
        # By config
        by_config = {}
        for r in results:
            key = (r['strategy'], r['use_rag'])
            if key not in by_config:
                by_config[key] = []
            by_config[key].append(r['features_f1'])
        
        best_config = max(by_config.items(), key=lambda x: statistics.mean(x[1]))
        config_name = f"{best_config[0][0].replace('zero_shot_', '').replace('_', ' ').title()} {'+ RAG' if best_config[0][1] else ''}"
        best_f1 = statistics.mean(best_config[1])
        
        print(f"{model_name:<15} & {overall_f1:>5.3f} & {config_name:<20} & {best_f1:>5.3f} \\\\")
    except FileNotFoundError:
        pass
