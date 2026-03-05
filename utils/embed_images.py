#!/usr/bin/env python3
"""
Project AWRA - Image to Base64 Converter
Converts PNG/JPG images to base64 and embeds them in the HTML file
"""

import base64
import os
from pathlib import Path

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    try:
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error reading {image_path}: {e}")
        return None

def get_mime_type(file_path):
    """Get MIME type based on file extension"""
    ext = Path(file_path).suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
    }
    return mime_types.get(ext, 'image/png')

def main():
    print("=" * 60)
    print("PROJECT AWRA - IMAGE EMBEDDER")
    print("Converts images to base64 and embeds them in HTML")
    print("=" * 60)
    
    # Define expected image paths (adjusted for utils/ folder)
    base_dir = Path(__file__).parent.parent / 'webapp' / 'assets'
    html_file = Path(__file__).parent.parent / 'webapp' / 'index_GAS.html'
    
    print(f"\n📁 Looking for images in: {base_dir}")
    
    images = {
        'logo': base_dir / 'ece_logo_cropped.png',
        'typhoon': base_dir / 'typhoon_satellite.png',
    }
    
    embedded_images = {}
    
    # Convert images to base64
    for name, img_path in images.items():
        if img_path.exists():
            print(f"\n✅ Found: {name.upper()}")
            print(f"   Path: {img_path}")
            b64 = image_to_base64(str(img_path))
            if b64:
                mime = get_mime_type(str(img_path))
                data_uri = f"data:{mime};base64,{b64}"
                embedded_images[name] = data_uri
                print(f"   ✓ Converted to base64 ({len(b64)} chars)")
        else:
            print(f"\n⚠️  Not found: {name.upper()}")
            print(f"   Expected: {img_path}")
            print(f"   Please place your image in the assets/ folder")
    
    if not embedded_images:
        print("\n❌ No images found. Please add your images to:")
        print(f"   - {base_dir / 'ece_logo_cropped.png'}")
        print(f"   - {base_dir / 'typhoon_satellite.png'}")
        return
    
    # Read HTML file
    if not html_file.exists():
        print(f"\n❌ HTML file not found: {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace placeholders
    updated = html_content
    replacements = 0
    
    if 'logo' in embedded_images:
        # Replace company logo src
        import re
        logo_pattern = r'id="company-logo"\s+src="[^"]*"'
        logo_replacement = f'id="company-logo" src="{embedded_images["logo"]}"'
        if re.search(logo_pattern, updated):
            updated = re.sub(logo_pattern, logo_replacement, updated)
            print(f"\n✓ Updated company logo in HTML")
            replacements += 1
    
    if 'typhoon' in embedded_images:
        # Replace typhoon image src
        import re
        typhoon_pattern = r'id="typhoon-image"\s+src="[^"]*"'
        typhoon_replacement = f'id="typhoon-image" src="{embedded_images["typhoon"]}"'
        if re.search(typhoon_pattern, updated):
            updated = re.sub(typhoon_pattern, typhoon_replacement, updated)
            print(f"✓ Updated typhoon image in HTML")
            replacements += 1
    
    if replacements > 0:
        # Write updated HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"\n✅ Successfully updated: {html_file}")
        print(f"   {replacements} image(s) embedded")
        print("\n📝 Next steps:")
        print("   1. Copy the updated index_GAS.html to your GAS project")
        print("   2. Refresh your dashboard")
        print("   3. Your logos are now permanently embedded! 🎉")
    else:
        print(f"\n⚠️  Could not find image placeholders in HTML")
        print(f"   Make sure the HTML has these IDs:")
        print(f"   - id='company-logo'")
        print(f"   - id='typhoon-image'")

if __name__ == '__main__':
    main()
