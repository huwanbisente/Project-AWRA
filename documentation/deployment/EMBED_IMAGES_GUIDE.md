# Embed Images in GAS Dashboard

## Quick Start (3 Steps)

### Step 1: Place Your Images in Assets Folder
Copy your image files to the `/webapp/assets/` folder:
```
webapp/
├── assets/
│   ├── ece_logo_cropped.png        ← Your company logo
│   ├── typhoon_satellite.png       ← Your typhoon/satellite image
│   └── (other assets...)
```

**Image Requirements:**
- **Logo**: PNG or JPG, any size (ideally square, 200x200+ recommended)
- **Typhoon**: PNG or JPG, preferably circular or square

### Step 2: Run the Embed Script
```bash
python3 embed_images.py
```

This will:
1. ✅ Find your images in `/webapp/assets/`
2. ✅ Convert them to base64
3. ✅ Automatically embed them in `index_GAS.html`

### Step 3: Deploy to GAS
1. Copy the updated `index_GAS.html` to your GAS project
2. Replace the existing `index.html`
3. Redeploy
4. Your logos are now permanently embedded! 🎉

---

## What the Script Does

The `embed_images.py` script:
- Finds your image files
- Converts them to base64 format
- Replaces placeholder URLs in the HTML
- Creates no-dependency embedded images

**Result:** Your logos are now built into the HTML - no URLs needed, no external dependencies!

---

## Manual Setup (If Script Doesn't Work)

If you prefer to manually embed images:

1. **Convert your image to base64** using any online tool:
   - Go to https://www.base64encode.org/
   - Upload your PNG/JPG file
   - Copy the base64 string

2. **Replace in HTML:**
   - Find: `<img id="company-logo" src="data:image/svg+xml,..."`
   - Replace the `src=` value with: `src="data:image/png;base64,PASTE_YOUR_BASE64_HERE"`

3. Repeat for typhoon image

---

## Troubleshooting

**Script says "Not found"?**
- Make sure image files are in `/webapp/assets/` folder
- Names should be exactly:
  - `ece_logo_cropped.png` (or .jpg)
  - `typhoon_satellite.png` (or .jpg)

**Images not showing after deployment?**
- Make sure you re-deployed the GAS project
- Refresh your browser cache (Ctrl+Shift+Delete)
- Check browser console (F12) for errors

**Want to change images later?**
- Replace the files in `/webapp/assets/`
- Run `python3 embed_images.py` again
- Update GAS with the new HTML file
- Redeploy

---

## Benefits

✅ **No URL dependencies** - Logos are built-in  
✅ **Faster loading** - No external requests  
✅ **Offline ready** - Works without internet  
✅ **Private** - Images not hosted anywhere  
✅ **Simple** - Just one command to update  

---

**Ready?** Run: `python3 embed_images.py` 🚀
