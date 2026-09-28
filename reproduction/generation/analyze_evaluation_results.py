"""
Analyze evaluation results from all models
Takes first 26 results from each model and generates detailed statistics
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics

# Models to analyze
MODELS = [
    'claude_sonnet_4_5',
    'claude_sonnet_3_7',
    'gemini_2_0_flash',
    'gpt_4o',
    'mistral_large',
    'llama_3_1_70b',
]

def analyze_model(checkpoint_file):
    """Analyze first 26 results from a model checkpoint"""
    with open(checkpoint_file, 'r') as f:
        data = json.load(f)
    
    results = data['results'][:26]  # Take only first 26
    
    stats = {
        'total_tests': len(results),
        'with_verify': {
            'valid_count': 0,
            'accuracies': [],
            'times': [],
            'attempts': [],
        },
        'no_verify': {
            'valid_count': 0,
            'accuracies': [],
            'times': [],
        },
        'improvements': [],
        'by_rag': {
            'with_rag': {'valid_with_verify': 0, 'valid_no_verify': 0, 'count': 0},
            'without_rag': {'valid_with_verify': 0, 'valid_no_verify': 0, 'count': 0},
        },
        'by_rhyme_type': defaultdict(lambda: {
            'valid_with_verify': 0,
            'valid_no_verify': 0,
            'count': 0,
            'accuracies_with_verify': [],
            'accuracies_no_verify': [],
        }),
        'by_features': defaultdict(lambda: {
            'valid_with_verify': 0,
            'valid_no_verify': 0,
            'count': 0,
            'accuracies_with_verify': [],
            'accuracies_no_verify': [],
        }),
    }
    
    for result in results:
        # With verification stats
        if result.get('with_verify_valid'):
            stats['with_verify']['valid_count'] += 1
        
        # Calculate accuracy if not provided
        with_verify_acc = result.get('with_verify_correct_pairs', 0) / max(result.get('with_verify_total_pairs', 1), 1) * 100
        no_verify_acc = result.get('no_verify_correct_pairs', 0) / max(result.get('no_verify_total_pairs', 1), 1) * 100
        
        stats['with_verify']['accuracies'].append(with_verify_acc)
        stats['with_verify']['times'].append(result.get('with_verify_time', 0))
        stats['with_verify']['attempts'].append(result.get('with_verify_attempts', 0))
        
        # No verification stats
        if result.get('no_verify_valid'):
            stats['no_verify']['valid_count'] += 1
        
        stats['no_verify']['accuracies'].append(no_verify_acc)
        stats['no_verify']['times'].append(result.get('no_verify_time', 0))
        
        # Improvement
        improvement = with_verify_acc - no_verify_acc
        stats['improvements'].append(improvement)
        
        # By RAG
        rag_key = 'with_rag' if result.get('use_rag') else 'without_rag'
        stats['by_rag'][rag_key]['count'] += 1
        if result.get('with_verify_valid'):
            stats['by_rag'][rag_key]['valid_with_verify'] += 1
        if result.get('no_verify_valid'):
            stats['by_rag'][rag_key]['valid_no_verify'] += 1
        
        # By rhyme type
        rhyme_type = result.get('rhyme_type', 'unknown')
        stats['by_rhyme_type'][rhyme_type]['count'] += 1
        if result.get('with_verify_valid'):
            stats['by_rhyme_type'][rhyme_type]['valid_with_verify'] += 1
        if result.get('no_verify_valid'):
            stats['by_rhyme_type'][rhyme_type]['valid_no_verify'] += 1
        stats['by_rhyme_type'][rhyme_type]['accuracies_with_verify'].append(with_verify_acc)
        stats['by_rhyme_type'][rhyme_type]['accuracies_no_verify'].append(no_verify_acc)
        
        # By features
        features = result.get('features', [])
        if not features:
            feature_key = 'BASIC (no features)'
        else:
            feature_key = '+'.join(sorted(features))
        
        stats['by_features'][feature_key]['count'] += 1
        if result.get('with_verify_valid'):
            stats['by_features'][feature_key]['valid_with_verify'] += 1
        if result.get('no_verify_valid'):
            stats['by_features'][feature_key]['valid_no_verify'] += 1
        stats['by_features'][feature_key]['accuracies_with_verify'].append(with_verify_acc)
        stats['by_features'][feature_key]['accuracies_no_verify'].append(no_verify_acc)
    
    return stats

def print_model_stats(model_name, stats):
    """Print detailed statistics for a model"""
    print(f"\n{'='*80}")
    print(f"MODEL: {model_name.replace('_', '-').upper()}")
    print(f"{'='*80}")
    
    print(f"\n📊 OVERALL STATISTICS (n={stats['total_tests']})")
    print(f"{'─'*80}")
    
    # With verification
    print(f"\n✓ WITH VERIFICATION:")
    print(f"  Valid poems: {stats['with_verify']['valid_count']}/{stats['total_tests']} ({stats['with_verify']['valid_count']/stats['total_tests']*100:.1f}%)")
    if stats['with_verify']['accuracies']:
        print(f"  Accuracy: {statistics.mean(stats['with_verify']['accuracies']):.1f}% (±{statistics.stdev(stats['with_verify']['accuracies']) if len(stats['with_verify']['accuracies']) > 1 else 0:.1f})")
        print(f"  Time: {statistics.mean(stats['with_verify']['times']):.1f}s (±{statistics.stdev(stats['with_verify']['times']) if len(stats['with_verify']['times']) > 1 else 0:.1f}s)")
        print(f"  Attempts: {statistics.mean(stats['with_verify']['attempts']):.1f} (±{statistics.stdev(stats['with_verify']['attempts']) if len(stats['with_verify']['attempts']) > 1 else 0:.1f})")
    
    # Without verification
    print(f"\n✗ WITHOUT VERIFICATION:")
    print(f"  Valid poems: {stats['no_verify']['valid_count']}/{stats['total_tests']} ({stats['no_verify']['valid_count']/stats['total_tests']*100:.1f}%)")
    if stats['no_verify']['accuracies']:
        print(f"  Accuracy: {statistics.mean(stats['no_verify']['accuracies']):.1f}% (±{statistics.stdev(stats['no_verify']['accuracies']) if len(stats['no_verify']['accuracies']) > 1 else 0:.1f})")
        print(f"  Time: {statistics.mean(stats['no_verify']['times']):.1f}s (±{statistics.stdev(stats['no_verify']['times']) if len(stats['no_verify']['times']) > 1 else 0:.1f}s)")
    
    # Improvement
    if stats['improvements']:
        print(f"\n📈 IMPROVEMENT FROM VERIFICATION:")
        print(f"  Average: {statistics.mean(stats['improvements']):.1f}% (±{statistics.stdev(stats['improvements']) if len(stats['improvements']) > 1 else 0:.1f}%)")
        print(f"  Median: {statistics.median(stats['improvements']):.1f}%")
        print(f"  Range: [{min(stats['improvements']):.1f}%, {max(stats['improvements']):.1f}%]")
    
    # By RAG
    print(f"\n🔍 BY RAG USAGE:")
    for rag_key, rag_stats in stats['by_rag'].items():
        if rag_stats['count'] > 0:
            print(f"\n  {rag_key.replace('_', ' ').upper()} (n={rag_stats['count']}):")
            print(f"    With verification valid: {rag_stats['valid_with_verify']}/{rag_stats['count']} ({rag_stats['valid_with_verify']/rag_stats['count']*100:.1f}%)")
            print(f"    Without verification valid: {rag_stats['valid_no_verify']}/{rag_stats['count']} ({rag_stats['valid_no_verify']/rag_stats['count']*100:.1f}%)")
    
    # By rhyme type
    print(f"\n📝 BY RHYME TYPE:")
    for rhyme_type, rhyme_stats in sorted(stats['by_rhyme_type'].items()):
        print(f"\n  {rhyme_type} (n={rhyme_stats['count']}):")
        print(f"    With verification valid: {rhyme_stats['valid_with_verify']}/{rhyme_stats['count']} ({rhyme_stats['valid_with_verify']/rhyme_stats['count']*100:.1f}%)")
        print(f"    Without verification valid: {rhyme_stats['valid_no_verify']}/{rhyme_stats['count']} ({rhyme_stats['valid_no_verify']/rhyme_stats['count']*100:.1f}%)")
        if rhyme_stats['accuracies_with_verify']:
            print(f"    Avg accuracy (with verify): {statistics.mean(rhyme_stats['accuracies_with_verify']):.1f}%")
            print(f"    Avg accuracy (no verify): {statistics.mean(rhyme_stats['accuracies_no_verify']):.1f}%")
    
    # By features
    print(f"\n🎯 BY FEATURES:")
    for feature_key, feature_stats in sorted(stats['by_features'].items()):
        print(f"\n  {feature_key} (n={feature_stats['count']}):")
        print(f"    With verification valid: {feature_stats['valid_with_verify']}/{feature_stats['count']} ({feature_stats['valid_with_verify']/feature_stats['count']*100:.1f}%)")
        print(f"    Without verification valid: {feature_stats['valid_no_verify']}/{feature_stats['count']} ({feature_stats['valid_no_verify']/feature_stats['count']*100:.1f}%)")
        if feature_stats['accuracies_with_verify']:
            print(f"    Avg accuracy (with verify): {statistics.mean(feature_stats['accuracies_with_verify']):.1f}%")
            print(f"    Avg accuracy (no verify): {statistics.mean(feature_stats['accuracies_no_verify']):.1f}%")

def main():
    print("="*80)
    print("EVALUATION RESULTS ANALYSIS")
    print("Analyzing first 26 results from each model")
    print("="*80)
    
    all_stats = {}
    
    for model in MODELS:
        checkpoint_file = f"checkpoint_{model}.json"
        if Path(checkpoint_file).exists():
            try:
                stats = analyze_model(checkpoint_file)
                all_stats[model] = stats
                print_model_stats(model, stats)
            except Exception as e:
                print(f"\n❌ Error analyzing {model}: {e}")
        else:
            print(f"\n⚠️  Checkpoint not found: {checkpoint_file}")
    
    # Comparative summary
    print(f"\n\n{'='*80}")
    print("COMPARATIVE SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n{'Model':<25} {'Valid (verify)':<15} {'Accuracy (verify)':<20} {'Improvement':<15}")
    print(f"{'─'*80}")
    
    for model, stats in all_stats.items():
        model_name = model.replace('_', '-')
        valid_pct = stats['with_verify']['valid_count']/stats['total_tests']*100
        avg_acc = statistics.mean(stats['with_verify']['accuracies']) if stats['with_verify']['accuracies'] else 0
        avg_imp = statistics.mean(stats['improvements']) if stats['improvements'] else 0
        print(f"{model_name:<25} {valid_pct:>6.1f}%          {avg_acc:>6.1f}%              {avg_imp:>+6.1f}%")
    
    print(f"\n{'='*80}")

if __name__ == "__main__":
    main()
