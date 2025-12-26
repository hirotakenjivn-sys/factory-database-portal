import chardet
import os

def check_encoding(file_path):
    # Try windows-1258 (Vietnamese)
    encodings = ['utf-8', 'windows-1258', 'cp932', 'iso-8859-1']
    
    with open(file_path, 'rb') as f:
        rawdata = f.read()
        
    for enc in encodings:
        try:
            print(f"--- Trying {enc} ---")
            content = rawdata.decode(enc)
            # Check for common Vietnamese chars or if '?' appears where it shouldn't
            if 'NISSEI' in content:
                print(f"--- Found NISSEI in {enc} ---")
                for line in content.splitlines():
                    if 'NISSEI' in line or 'SHARP' in line:
                        print(f"Line: {line.strip()}")
        except Exception as e:
            print(f"Failed with {enc}: {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'product-list.csv')
    check_encoding(csv_path)
