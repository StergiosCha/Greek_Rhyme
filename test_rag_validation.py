from rag_system import validate_corpus
import json

print("Validating Rhyme Corpus...")
report = validate_corpus()

print(f"Valid: {report['valid']}")
print(f"Invalid: {report['invalid']}")

if report['invalid'] > 0:
    print("\nInvalid Examples Details:")
    print(json.dumps(report['details'], indent=2, ensure_ascii=False))
