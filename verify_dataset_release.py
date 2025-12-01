import json
import os
from pathlib import Path

def verify_datasets(base_dir):
    json_dir = Path(base_dir) / "json"
    raw_text_dir = Path(base_dir) / "raw_text"
    
    print(f"Verifying datasets in {base_dir}...")
    
    # Check if directories exist
    if not json_dir.exists():
        print(f"❌ JSON directory missing: {json_dir}")
        return
    if not raw_text_dir.exists():
        print(f"❌ Raw text directory missing: {raw_text_dir}")
        return
        
    # Verify JSON files
    for json_file in json_dir.glob("*.json"):
        print(f"\nChecking {json_file.name}...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check structure
            if not data:
                print("  ❌ Empty JSON file")
                continue
                
            # Determine if it's a base or enhanced corpus
            if "version" in data and "enhanced" in data["version"]:
                # Enhanced Corpus Structure
                poet_name = data.get("poet", "Unknown")
                source_path = data.get("source", "")
                total_count = data.get("total_entries", 0)
                print(f"  ✓ Enhanced Corpus Structure valid (Poet: {poet_name})")
            else:
                # Base Corpus Structure
                # Get the first key (Poet Name)
                poet_key = list(data.keys())[0]
                poet_data = data[poet_key]
                poet_name = poet_data.get("poet", "Unknown")
                source_path = poet_data.get("source", "")
                total_count = poet_data.get("total_rhymes", 0)
                print(f"  ✓ Base Corpus Structure valid (Poet: {poet_name})")

            print(f"  ✓ Found {total_count} rhymes")
            
            # Verify source file exists
            if not source_path:
                 print("  ❌ Source path missing")
                 continue

            # The source path in JSON might be relative to the original project root (e.g. "Data/file.txt")
            # We need to check if the corresponding file exists in our new raw_text dir
            source_filename = Path(source_path).name
            new_source_path = raw_text_dir / source_filename
            
            if new_source_path.exists():
                print(f"  ✓ Source file found: {source_filename}")
            else:
                print(f"  ⚠️  Source file missing in raw_text: {source_filename}")
                    
        except json.JSONDecodeError:
            print("  ❌ Invalid JSON format")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    verify_datasets("greek_rhyme_dataset")
