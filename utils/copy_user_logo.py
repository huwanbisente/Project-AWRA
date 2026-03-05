
import shutil
import os

# Source path from the user upload
src_path = r"C:/Users/Vincent/.gemini/antigravity/brain/2f3e2a59-62cb-4aae-a41b-396566309116/uploaded_media_1770247629582.png"

# Dest path
dest_path = r"f:/for PORTFOLIO/ECE_Project_AWRA/webapp/assets/ece_exact_logo.png"

try:
    # Ensure dir exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    shutil.copy(src_path, dest_path)
    print(f"✅ Copied Exact User Logo to {dest_path}")
except Exception as e:
    print(f"❌ Error copying image: {e}")
