# QUICK START: Deploy AWRA Dashboard to GAS

## ⚡ 5-Minute Quick Start

### What You Need
- Google Account
- Your `summary.json` file ID from Google Drive
- The two fixed files: `Code_GAS.gs` and `index_GAS.html`

### Step 1: Get Your File ID (1 min)
1. Go to Google Drive
2. Find your `summary.json` file
3. Right-click → Share → Get link
4. Copy the ID from URL: `https://drive.google.com/file/d/**[ID HERE]**/view`

### Step 2: Update Backend Code (1 min)
1. Open `Code_GAS.gs`
2. Find this line: `const DATA_FILE_ID = '1gLJCM7RvnuOOBzS34N2QmU8jNYUFnVlN';`
3. Replace with your ID
4. Save

### Step 3: Create GAS Project (1 min)
1. Go to script.google.com
2. Click "New project"
3. Name it: `Project AWRA Dashboard`

### Step 4: Add Code (1 min)
1. Delete placeholder code
2. Copy all of `Code_GAS.gs` → paste into `Code.gs`
3. Click **"+ New"** → **"HTML file"**
4. Name it: `index`
5. Copy all of `index_GAS.html` → paste into `index.html`

### Step 5: Deploy (1 min)
1. Click **"Deploy"** → **"New deployment"**
2. Select **"Web app"**
3. Execute as: Your email
4. Who has access: **Anyone**
5. Click **"Deploy"**
6. Authorize when prompted
7. **Copy the Web App URL** - this is your dashboard!

---

## ✅ Verify It Works

1. Visit the Web App URL
2. Should see dashboard loading with data
3. If blank: Check browser console (F12) for errors

## 🔧 Common Fixes

| Problem | Fix |
|---------|-----|
| "Could not access data file" | Update DATA_FILE_ID, share file publicly |
| Blank page | Refresh page, check console for errors |
| "Authorization required" | Re-deploy, set access to "Anyone" |

## 📚 Full Guide
See `GAS_DEPLOYMENT_GUIDE.md` for detailed instructions

## 💡 Pro Tips
- Test locally first: Open `index_GAS.html` in browser with `summary.json` nearby
- Update `summary.json` anytime - dashboard auto-fetches latest
- Share only the Web App URL, not the Script editor link
- No redeploy needed after updating data

---

**Status**: Ready to Deploy ✅  
**Time to Deploy**: ~5 minutes  
**Difficulty**: Easy (No coding needed!)
