# How to Add Your Logo & Typhoon Image to GAS Dashboard

## Quick Steps

### 1. Upload Your Images to Google Drive
1. Go to **Google Drive** (drive.google.com)
2. Create a new folder called "Dashboard Assets"
3. Upload your logo and typhoon image files

### 2. Share the Images Publicly
For each image:
1. Right-click the file
2. Click **Share**
3. Change to **"Anyone with the link can view"**
4. Copy the file ID from the share link

### 3. Get the Public Image URL

For a Google Drive image, the URL format is:
```
https://drive.google.com/uc?export=view&id=FILE_ID_HERE
```

Replace `FILE_ID_HERE` with the actual file ID.

**Example:**
- Share link: `https://drive.google.com/file/d/1abc123xyz/view?usp=sharing`
- File ID: `1abc123xyz`
- Image URL: `https://drive.google.com/uc?export=view&id=1abc123xyz`

### 4. Add Images to Dashboard

1. Visit your Project AWRA dashboard
2. Click the **⚙️ Settings** button in the footer
3. Paste your image URLs:
   - **Company Logo URL** → Your ECE logo
   - **Typhoon Monitor Icon URL** → Your typhoon/satellite image
4. Click **Save Settings**
5. **Refresh the page** (F5)

## Tips

✅ **Logo Requirements:**
- Square format works best (e.g., 200x200px)
- PNG with transparency recommended
- Can be any size - it will scale to fit

✅ **Typhoon Image Requirements:**
- Should be a circular/round image if possible
- Will rotate continuously (12-second full rotation)
- Size: 48x48px in the display

✅ **URL Tips:**
- Always use the `https://drive.google.com/uc?export=view&id=...` format
- Don't use the regular sharing link - it won't work as an image
- Make sure the file is publicly shared

## Troubleshooting

**Images Not Showing?**
1. Check that the Google Drive file is **publicly shared**
2. Verify the URL is correct (use the `uc?export=view` format)
3. Open the URL in a new tab - should display the image directly
4. If it opens a preview page instead, the URL format is wrong

**URL Doesn't Work?**
- Go to Google Drive → Right-click image → Open in new tab
- Copy the actual image file ID from the URL bar
- Use this format: `https://drive.google.com/uc?export=view&id=YOUR_FILE_ID`

## Example

**If your Google Drive share link is:**
```
https://drive.google.com/file/d/1_6GxDSGslIcjCabe-4JzxpRuN4WIRnXj/view?usp=sharing
```

**Your image URL should be:**
```
https://drive.google.com/uc?export=view&id=1_6GxDSGslIcjCabe-4JzxpRuN4WIRnXj
```

---

## Storage Location

Settings are saved in your browser's **local storage**, so:
- ✅ Settings persist even if you close the browser
- ✅ Each browser/device remembers your settings
- ⚠️ Clearing browser cache will reset settings
- ⚠️ Different browsers will have different saved settings

**Pro Tip:** Save your image URLs somewhere safe so you can quickly restore them if needed!
