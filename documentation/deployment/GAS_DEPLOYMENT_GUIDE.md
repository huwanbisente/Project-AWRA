# GAS Deployment Guide - Project AWRA Dashboard

## Overview

This guide explains how to fix and deploy the Project AWRA dashboard to Google Apps Script (GAS).

## Files You Need

Two critical files have been created for GAS deployment:

1. **Code_GAS.gs** - The backend Google Apps Script
2. **index_GAS.html** - The frontend HTML interface

## Step-by-Step Deployment

### Step 1: Prepare Your Google Drive

1. Upload your latest `summary.json` file to Google Drive
2. **IMPORTANT**: Right-click the file → Share → Get link
3. Copy the file ID from the URL:
   - **URL format**: `https://drive.google.com/file/d/{FILE_ID}/view`
   - **Example**: If URL is `https://drive.google.com/file/d/1gLJCM7RvnuOOBzS34N2QmU8jNYUFnVlN/view`
   - Then FILE_ID = `1gLJCM7RvnuOOBzS34N2QmU8jNYUFnVlN`

4. Make sure the file is **shared with "Anyone with the link can view"** or your GAS script won't have access

### Step 2: Set Up Google Apps Script Project

1. Go to **[script.google.com](https://script.google.com/)**
2. Click **"New project"**
3. Name it: `Project AWRA Dashboard`
4. You should see a blank `Code.gs` file

### Step 3: Add Backend Code

1. Delete the placeholder code in `Code.gs`
2. Open [Code_GAS.gs](./Code_GAS.gs) from this folder
3. **Copy the entire contents** and paste it into the `Code.gs` file in the Google Apps Script editor
4. **CRITICAL**: Find this line:
   ```javascript
   const DATA_FILE_ID = '1gLJCM7RvnuOOBzS34N2QmU8jNYUFnVlN'; 
   ```
5. Replace `1gLJCM7RvnuOOBzS34N2QmU8jNYUFnVlN` with YOUR file ID from Step 1
6. Save the file (Ctrl+S)

### Step 4: Add Frontend HTML

1. In the Google Apps Script editor, click **"+ New"** → **"HTML file"**
2. Name it exactly: `index` (GAS requires this specific name)
3. Delete the placeholder code
4. Open [index_GAS.html](./index_GAS.html) from this folder
5. **Copy all contents** and paste into the new HTML file
6. Save the file (Ctrl+S)

### Step 5: Deploy as Web App

1. Click **"Deploy"** in the top-right corner
2. Select **"New deployment"**
3. Click the dropdown and select **"Web app"**
4. Configure:
   - **Execute as**: Your email address (e.g., yourname@gmail.com) ← CRITICAL
   - **Who has access**: Anyone
5. Click **"Deploy"**
6. A popup will ask for permissions:
   - Click **"Review permissions"**
   - Select your Google account
   - Click **"Advanced"**
   - Click **"Go to Project AWRA Dashboard (unsafe)"** - this is normal, it's your own project
   - Click **"Allow"**

### Step 6: Get Your Public URL

After deployment succeeds:
1. You'll see a dialog with "Deployment successful"
2. Copy the **Web app URL** (looks like: `https://script.google.com/macros/d/.../usercopy`)
3. **This is your public dashboard link** - share this with anyone
4. Anyone with this link can view the dashboard without logging in

## Troubleshooting

### "Could not access data file" Error

**Cause**: The DATA_FILE_ID is incorrect or the file isn't shared properly

**Fix**:
1. Double-check the file ID matches your summary.json file exactly
2. Ensure the file is shared: Right-click file → Share → "Anyone with the link can view"
3. Re-deploy with correct file ID (Deploy → New deployment)

### Blank Dashboard or Missing Data

**Cause**: GAS script can't reach Google Drive file

**Fix**:
1. Test the connection:
   - In Google Apps Script editor, go to **View** → **Logs**
   - Run the script: Click **function** dropdown → Select `testConnection` → Run
   - Check logs for "Data fetch successful"
2. If it fails, the file sharing settings are wrong

### "Authorization required" When Visiting URL

**Cause**: Deployment wasn't set to "Anyone" access

**Fix**:
1. Go back to Google Apps Script
2. Click **"Deploy"** → **"Manage deployments"**
3. Edit the deployment and change **"Who has access"** to **"Anyone"**
4. The page should now load without login

### Images Not Showing

**Cause**: GAS can't serve local image files

**Status**: The current version uses placeholder colors instead of actual logos, which works fine. If you have hosted image URLs, you can update the HTML file to reference them.

## How It Works

```
Your summary.json in Google Drive
           ↓
    Code.gs (Backend)
           ↓
    getData() function retrieves the JSON
           ↓
    index.html (Frontend)
           ↓
    google.script.run.getData() calls backend
           ↓
    Dashboard displays live data
```

## Updating Dashboard Data

1. Update your `summary.json` file in Google Drive
2. The dashboard fetches fresh data every time someone visits the URL
3. **No need to redeploy** - it reads the latest file automatically

## Testing Locally (Before GAS)

If you want to test the dashboard locally first:

1. Place `summary.json` in the same folder as `index_GAS.html`
2. Open `index_GAS.html` in a browser
3. The script detects "no GAS environment" and loads from local file
4. This lets you verify the dashboard works before deploying

## Important Notes

- **Always use the web app URL** for sharing, not the source Script editor link
- The DATA_FILE_ID points to a read-only snapshot - it won't auto-sync hourly, only when the file changes in Drive
- For best results, update `summary.json` regularly and the dashboard will fetch the latest version automatically
- The dashboard works in modern browsers (Chrome, Firefox, Edge, Safari)

## Support

If you encounter issues:

1. Check the **Apps Script logs** (View → Logs) for error messages
2. Verify your **DATA_FILE_ID** is correct
3. Ensure your **summary.json is shared** publicly
4. Test with the **testConnection()** function
5. Clear browser cache and refresh the URL

---

**Version**: Project AWRA v1.0 (GAS Ready)  
**Last Updated**: February 5, 2026
