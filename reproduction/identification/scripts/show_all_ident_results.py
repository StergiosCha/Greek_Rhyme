import json
import statistics

models = {
    'Claude 4.5': 'identification_results_claude_sonnet_4.5.json',
    'Claude 3.7': 'identification_results_claude_sonnet_3.7_FIXED.json',
    'GPT-4o': 'identification_results_gpt_4o.json',
    'Gemini 2.0': 'identification_results_gemini_2.0_flash.json',
    'Llama 3.1 70B': 'identification_results_llama_3.1_70b.json',
    'Llama 3.3 70B': 'identification_results_llama_3.3_70b.json',
    'Mistral Large': 'identification_results_mistral_large.json',
    'Llama 3.1 8B': 'identification_results_llama_3.1_8b.json'
}

print('='*100)
print('COMPLETE IDENTIFICATION RESULTS - ALL CONFIGURATIONS')
print('='*100)
print(f"{'Model':<15} {'Strategy':<20} {'RAG':<8} {'Rhyme Type':<12} {'Feature F1':<12}")
print('-'*100)

for model_name, filename in models.items():
    try:
        with open(filename) as f:
            results = json.load(f)
        
        # Group by strategy and RAG
        configs = {}
        for r in results:
            key = (r['strategy'], r['use_rag'])
            if key not in configs:
                configs[key] = []
            configs[key].append(r)
        
        # Print each configuration
        for (strategy, use_rag), res_list in sorted(configs.items()):
            rt_acc = sum(r['rhyme_type_correct'] for r in res_list) / len(res_list) * 100
            f1 = statistics.mean(r['features_f1'] for r in res_list)
            rag_str = 'WITH' if use_rag else 'NO'
            print(f'{model_name:<15} {strategy:<20} {rag_str:<8} {rt_acc:>6.1f}%     {f1:>6.3f}')
        print()
    except FileNotFoundError:
        print(f'{model_name:<15} NOT FOUND')
        print()
