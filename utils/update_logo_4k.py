
import shutil
import os

# New 4k source path
src_path = r"C:/Users/Vincent/.gemini/antigravity/brain/2f3e2a59-62cb-4aae-a41b-396566309116/ece_logo_4k_white_bg_1770248111382.png"

# Dest path
dest_path = r"f:/for PORTFOLIO/ECE_Project_AWRA/webapp/assets/ece_logo_4k.png"

try:
    shutil.copy(src_path, dest_path)
    print(f"✅ Copied 4K Logo to {dest_path}")
except Exception as e:
    print(f"❌ Error copying image: {e}")
