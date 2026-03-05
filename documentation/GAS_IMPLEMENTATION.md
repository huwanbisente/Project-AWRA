# Google Apps Script Implementation Guide

## Overview
This guide explains how to deploy your Project AWRA Dashboard on Google Apps Script (GAS).

## 1. Setup Google Apps Script
1. Go to [script.google.com](https://script.google.com/) and create a **New Project**.
2. Name it "Project AWRA Dashboard".

## 2. Create `Code.gs` (Backend)
Copy and paste this into the `Code.gs` file. This script serves the HTML and fetches the data from your JSON file in Google Drive.

```javascript
// REPLACE THIS WITH THE FILE ID OF YOUR 'summary.json' IN GOOGLE DRIVE
const DATA_FILE_ID = 'YOUR_GOOGLE_DRIVE_FILE_ID_HERE';

function doGet() {
  return HtmlService.createTemplateFromFile('index')
      .evaluate()
      .setTitle('Project AWRA Dashboard')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
      .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function getData() {
  try {
    const file = DriveApp.getFileById(DATA_FILE_ID);
    const jsonContent = file.getBlob().getDataAsString();
    return jsonContent; // Returns the JSON string directly
  } catch (e) {
    Logger.log("Error fetching data: " + e.toString());
    return JSON.stringify({ error: e.toString() });
  }
}
```

## 3. Create `index.html` (Frontend)
Create a new HTML file in GAS named `index.html` and paste your dashboard code.
**Crucial Change:** You must replace the `init()` function with the GAS-compatible version below.

### Find this part in your code:
```javascript
async function init() {
    try {
        const res = await fetch('summary.json');
        const data = await res.json();
        globalData = data;
        // ... rest of the code
```

### Replace it with this:
```javascript
function init() {
    google.script.run
        .withSuccessHandler(function(jsonString) {
            try {
                const data = JSON.parse(jsonString);
                globalData = data;
                
                // --- PASTE THE REST OF YOUR RENDERING LOGIC HERE ---
                // (Update text, icons, forecasts, alerts, etc.)
                updateDashboardUI(data); 

            } catch (e) { console.error("Parse Error", e); }
        })
        .withFailureHandler(function(err) {
            console.error("GAS Server Error", err);
        })
        .getData(); // Calls the backend function
}

// Move all your UI updating logic into this separate function to keep it clean
function updateDashboardUI(data) {
     document.getElementById('last-updated').innerText = data.summary_of_current_conditions?.date?.toUpperCase() || "--";
     // ... copy all the lines from your previous init() function here ...
     // ...
}
```

## 4. Handle Images (Important)
Local images like `assets/ece_logo_cropped.png` **will not work**. You have two options:
1.  **Host them externally** (e.g., Imgur, or a public bucket) and use the full URL.
2.  **Base64 Encode** them and embed them directly in the `src` tag.
    *   Example: `<img src="data:image/png;base64,iVBORw0KGgo..." ...>`

## 5. Deployment (No-Login Setup)
1.  Click **Deploy** > **New Deployment**.
2.  Select **Web App**.
3.  **Execute as**: Set to **"Me"** (Your Email). *CRITICAL: This allows users to bypass sign-in.*
4.  **Who has access**: Set to **"Anyone"**.
5.  Click **Deploy**.
6.  **Authorize**: Click "Review Permissions" > Select your account > "Advanced" > "Go to Project AWRA (unsafe)" > "Allow".
7.  Copy the **Web App URL**. Anyone with this link can now see the dashboard without logging in!
