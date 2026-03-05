
import shutil
import os

# New Source paths from the generation tool output
ece_src = r"C:/Users/Vincent/.gemini/antigravity/brain/2f3e2a59-62cb-4aae-a41b-396566309116/ece_logo_transparent_1770247386386.png"
awra_src = r"C:/Users/Vincent/.gemini/antigravity/brain/2f3e2a59-62cb-4aae-a41b-396566309116/awra_logo_transparent_1770247401344.png"

# Dest paths (Overwriting previous ones)
ece_dest = r"f:/for PORTFOLIO/ECE_Project_AWRA/webapp/assets/ece_logo.png"
awra_dest = r"f:/for PORTFOLIO/ECE_Project_AWRA/webapp/assets/awra_logo.png"

try:
    shutil.copy(ece_src, ece_dest)
    print(f"✅ Updated ECE Logo to {ece_dest}")
    shutil.copy(awra_src, awra_dest)
    print(f"✅ Updated AWRA Logo to {awra_dest}")
except Exception as e:
    print(f"❌ Error copying images: {e}")
