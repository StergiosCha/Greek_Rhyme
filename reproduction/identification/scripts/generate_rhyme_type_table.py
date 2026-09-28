import json
import statistics

# Identification by rhyme type
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
print("IDENTIFICATION BY RHYME TYPE")
print("="*80)
print(f"{'Model':<15} {'M (n=32)':<12} {'F2 (n=40)':<12} {'F3 (n=32)':<12}")
print("-"*80)

for model_name, filename in models.items():
    try:
        with open(filename) as f:
            results = json.load(f)
        
        by_type = {}
        for r in results:
            rt = r['true_rhyme_type']
            if rt not in by_type:
                by_type[rt] = []
            by_type[rt].append(r['rhyme_type_correct'])
        
        m_acc = sum(by_type.get('M', [])) / len(by_type.get('M', [1])) * 100 if 'M' in by_type else 0
        f2_acc = sum(by_type.get('F2', [])) / len(by_type.get('F2', [1])) * 100 if 'F2' in by_type else 0
        f3_acc = sum(by_type.get('F3', [])) / len(by_type.get('F3', [1])) * 100 if 'F3' in by_type else 0
        
        print(f"{model_name:<15} {m_acc:>6.1f}%     {f2_acc:>6.1f}%      {f3_acc:>6.1f}%")
    except FileNotFoundError:
        print(f"{model_name:<15} NOT FOUND")

print("\n" + "="*80)
print("LATEX TABLE FORMAT")
print("="*80)

for model_name, filename in models.items():
    try:
        with open(filename) as f:
            results = json.load(f)
        
        by_type = {}
        for r in results:
            rt = r['true_rhyme_type']
            if rt not in by_type:
                by_type[rt] = []
            by_type[rt].append(r['rhyme_type_correct'])
        
        m_acc = sum(by_type.get('M', [])) / len(by_type.get('M', [1])) * 100 if 'M' in by_type else 0
        f2_acc = sum(by_type.get('F2', [])) / len(by_type.get('F2', [1])) * 100 if 'F2' in by_type else 0
        f3_acc = sum(by_type.get('F3', [])) / len(by_type.get('F3', [1])) * 100 if 'F3' in by_type else 0
        
        print(f"{model_name:<15} & {m_acc:>5.1f}\\% & {f2_acc:>5.1f}\\% & {f3_acc:>5.1f}\\% \\\\")
    except FileNotFoundError:
        pass
