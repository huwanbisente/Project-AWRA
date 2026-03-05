
from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

src = r"f:/for PORTFOLIO/ECE_Project_AWRA/webapp/assets/ece_logo_4k.png"
dest = r"f:/for PORTFOLIO/ECE_Project_AWRA/webapp/assets/ece_logo_cropped.png"

try:
    img = Image.open(src)
    # Trim logic
    img = trim(img)
    img.save(dest)
    print(f"✅ Cropped logo saved to {dest}")
except Exception as e:
    print(f"❌ Error cropping image: {e}")
