import marshal
import dis
import sys
import time

def recover(pyc_path, output_path):
    try:
        with open(pyc_path, 'rb') as f:
            # Skip header (16 bytes for Python 3.11 usually, but let's try standard skip)
            f.seek(16)
            code_obj = marshal.load(f)
            
        with open(output_path, 'w') as out:
            # Redirect stdout to file for dis.dis
            sys.stdout = out
            print(f"# Disassembly of {pyc_path}")
            print(f"# Constants: {code_obj.co_consts}")
            print(f"# Names: {code_obj.co_names}")
            print("-" * 40)
            dis.dis(code_obj)
            sys.stdout = sys.__stdout__
            
        print(f"Successfully disassembled to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    recover('__pycache__/phonology.cpython-311.pyc', 'phonology_disassembly.txt')
