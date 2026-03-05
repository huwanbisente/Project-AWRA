/**
 * PROJECT AWRA - GOOGLE APPS SCRIPT (GAS) BACKEND
 * Deployed as Web App - No Authentication Required
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to script.google.com and create a new project
 * 2. Replace DATA_FILE_ID with your summary.json file ID from Google Drive
 * 3. Copy this entire code into Code.gs
 * 4. Deploy as Web App (Execute as: Me, Who has access: Anyone)
 */

// ===== CRITICAL CONFIGURATION =====
// Replace with your Google Drive file ID containing summary.json
const DATA_FILE_ID = '1_6GxDSGslIcjCabe-4JzxpRuN4WIRnXj'; // YOUR GOOGLE DRIVE FILE ID HERE

// [OPTIONAL] Replace with a Google Sheet ID to log 
const LOG_SHEET_ID = '1uEOOm_PM7Cgc6a3KLWOgzqOM9RTDFXSBN8_xOWRkcIY'; 


/**
 * Main entry point - serves the HTML interface
 * Called automatically when user visits the web app URL
 */   
 
function doGet() {
  try {
    return HtmlService.createTemplateFromFile('index')
        .evaluate()
        .setTitle('Project AWRA - Operations Dashboard')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
        .addMetaTag('viewport', 'width=device-width, initial-scale=1')
        .setWidth(1920)
        .setHeight(1080);
  } catch (e) {
    return HtmlService.createHtmlOutput(`<p>Error loading dashboard: ${e.toString()}</p>`);
  }
}

/**
 * Fetches raw JSON data from Google Drive file
 * Called by frontend via google.script.run.getData()
 * 
 * @return {String} Raw JSON content as string
 */
function getData() {
  try {
    if (!DATA_FILE_ID || DATA_FILE_ID === 'YOUR_GOOGLE_DRIVE_FILE_ID_HERE') {
      throw new Error('DATA_FILE_ID not configured. Please update the constant at the top of Code.gs');
    }
    
    const file = DriveApp.getFileById(DATA_FILE_ID);
    const jsonContent = file.getBlob().getDataAsString();
    
    // Validate it's valid JSON
    try {
      JSON.parse(jsonContent);
    } catch (parseError) {
      throw new Error('File content is not valid JSON: ' + parseError.message);
    }
    
    return jsonContent;
  } catch (e) {
    Logger.log('Critical Data Fetch Error: ' + e.toString());
    const errorResponse = {
      error: 'Could not access data file',
      message: e.toString(),
      fileId: DATA_FILE_ID
    };
    return JSON.stringify(errorResponse);
  }
}

/**
 * Test function - call from Apps Script editor to verify setup
 * Logs the first 500 chars of data to check connectivity
 */
function testConnection() {
  const data = getData();
  Logger.log('Data fetch successful. First 500 characters:');
  Logger.log(data.substring(0, 500));
}

/**
 * Run this function in the editor to Authorize the script
 * and test if logging works.
 */
function testLogging() {
  Logger.log('Testing logging...');
  logVisit({
    userAgent: 'Test Editor',
    screen: 'N/A',
    language: 'en',
    timeZone: 'UTC'
  });
  Logger.log('Log entry sent. Check your spreadsheet.');
}

/**
 * Logs visitor details to a Google Sheet
 * @param {Object} info Visitor information from client
 */
function logVisit(info) {
  if (!LOG_SHEET_ID) return; // Skip if no sheet configured
  
  try {
    const doc = SpreadsheetApp.openById(LOG_SHEET_ID);
    const sheet = doc.getSheets()[0]; // Log to first sheet
    
    // Append a new row with timestamp and details
    sheet.appendRow([
      new Date(),                                   // Timestamp
      info.userAgent || 'Unknown',                 // Browser/Device
      info.screen || 'Unknown',                    // Screen Size
      info.language || 'Unknown',                  // Language
      info.timeZone || 'Unknown',                  // Timezone
      Session.getTemporaryActiveUserKey() || 'Anon' // Pseudo-ID
    ]);
    
  } catch (e) {
    Logger.log('Logging Error: ' + e.toString());
  }
}
