import os
import urllib.request
import sys

def download_assets():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonts_dir = os.path.join(base_dir, 'assets', 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Font Inter
    font_url = "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.ttf"
    font_bold_url = "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.ttf"
    font_path = os.path.join(fonts_dir, "Inter-Regular.ttf")
    font_bold_path = os.path.join(fonts_dir, "Inter-Bold.ttf")
    
    print("Mendownload font...")
    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(font_url, font_path)
            urllib.request.urlretrieve(font_bold_url, font_bold_path)
            print("Font Inter berhasil diunduh.")
        except Exception as e:
            print(f"Gagal mengunduh Font: {e}")

if __name__ == "__main__":
    # Paksa stdout untuk bisa menangani karakter Unicode agar tidak error di Windows
    sys.stdout.reconfigure(encoding='utf-8')
    download_assets()
