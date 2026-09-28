"""
Extract the valid test poems from Claude 3.7 run to create a Golden Test Set
"""
import json

SOURCE_CHECKPOINT = "identification_checkpoint_claude_sonnet_3.7.json"
OUTPUT_FILE = "golden_test_set.json"

def create_golden_set():
    print(f"Loading {SOURCE_CHECKPOINT}...")
    with open(SOURCE_CHECKPOINT, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # The checkpoint stores 'test_poems' which is the list of dicts
    test_poems = data.get('test_poems', [])
    
    if not test_poems:
        print("❌ No test poems found in checkpoint!")
        return
        
    print(f"Found {len(test_poems)} test poems.")
    
    # Save to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(test_poems, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Saved 'golden_test_set.json' with {len(test_poems)} poems.")

if __name__ == "__main__":
    create_golden_set()
