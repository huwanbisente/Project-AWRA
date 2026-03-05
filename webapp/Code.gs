/**
 * PROJECT AWRA / REMEDY DASHBOARD - BACKEND (Code.gs)
 * 
 * INSTRUCTIONS:
 * 1. Copy this entire code and paste it into the 'Code.gs' file in your Google Apps Script editor.
 * 2. Replace the 'DATA_FILE_ID' below with the ID of your 'summary.json' file in Google Drive.
 * 3. Deploy as a Web App (Execute as: Me, Who has access: Anyone).
 */

// REPLACE THIS ID with the one for your specific account
const DATA_FILE_ID = '1_6GxDSGslIcjCabe-4JzxpRuN4WIRnXj';

function doGet() {
  // This serves your HTML file. Ensure your HTML file is named 'index.html' in the GAS editor.
  return HtmlService.createTemplateFromFile('index')
      .evaluate()
      .setTitle('Operations Dashboard | Live Feed')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
      .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/**
 * Fetches the raw JSON data from the specified Google Drive file.
 * Called by the frontend init() function.
 */
function getData() {
  try {
    const file = DriveApp.getFileById(DATA_FILE_ID);
    const jsonContent = file.getBlob().getDataAsString();
    return jsonContent; 
  } catch (e) {
    console.error("Critical Data Fetch Error: " + e.toString());
    return JSON.stringify({ 
      error: "Could not access data file. Please check file ID and permissions.",
      details: e.toString() 
    });
  }
}
