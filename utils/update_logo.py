
import shutil
import os

# New Enhanced source path
src_path = r"C:/Users/Vincent/.gemini/antigravity/brain/2f3e2a59-62cb-4aae-a41b-396566309116/ece_logo_enhanced_1770247789826.png"

# Dest path
dest_path = r"f:/for PORTFOLIO/ECE_Project_AWRA/webapp/assets/ece_logo_hd.png"

try:
    shutil.copy(src_path, dest_path)
    print(f"✅ Copied Enhanced Logo to {dest_path}")
except Exception as e:
    print(f"❌ Error copying image: {e}")
