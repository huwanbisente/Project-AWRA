// ------------------------------------------------------------------
// PART 1: PARSE PAGASA TEXT (From HTML Extract Node)
// ------------------------------------------------------------------
// Input: items[0].json.data (extracted text from body)
const rawText = items[0].json.data || "";

// Extract "Metro Manila" and "Dumaguete" sections if possible, 
// or just clean up the text for the LLM.
// Since the prompt does the heavy lifting, we mainly need to ensure 
// we didn't capture navigational junk.

const cleanedText = rawText
  .replace("Skip to main content", "")
  .replace("Toggle navigation", "")
  .trim();

return [{
  json: {
    source: "PAGASA_WEBSITE",
    content: cleanedText
  }
}];

// ------------------------------------------------------------------
// PART 2: PARSE ACCUWEATHER (From HTML Extract)
// ------------------------------------------------------------------
// Input: items (Array of objects with max_temp, min_temp, etc.)
// We need to structure this into a readable string for the LLM.

let accuString = "ACCUWEATHER 10-DAY FORECAST:\n";

for (const item of items) {
  const date = item.json.date || "Unknown Date";
  const max = item.json.max_temp || "N/A";
  const min = item.json.min_temp || "N/A";
  const pop = item.json.pop || "0%";
  const desc = item.json.description || "";

  accuString += `Date: ${date} | High: ${max} | Low: ${min} | Rain: ${pop} | ${desc}\n`;
}

return [{
  json: {
    source: "ACCUWEATHER",
    content: accuString
  }
}];

// ------------------------------------------------------------------
// PART 3: AGGREGATE & PREPARE PROMPT (Master Aggregator)
// ------------------------------------------------------------------
// This script pulls data from ALL upstream nodes (PAGASA, AccuWeather, PDF).
// It uses n8n's $("NodeName") syntax to be independent of wiring order.

let pagasaText = "No PAGASA data available.";
let accuText = "No AccuWeather data available.";
let pdfText = "No PDF data available.";

// 1. SAFELY GET PAGASA TEXT
try {
  // Tries to read from 'Extract PAGASA Text' node (fallback workflow)
  // OR 'Scrape PAGASA' (puppeteer workflow)
  const pagasaNode = $('Extract PAGASA Text').first() || $('Scrape PAGASA').first();
  if (pagasaNode && pagasaNode.json) {
    // Use .data (HTML Extract) or .text (Puppeteer) or .content (Custom)
    pagasaText = pagasaNode.json.data || pagasaNode.json.text || pagasaNode.json.content || JSON.stringify(pagasaNode.json);
  }
} catch (error) {
  // Node likely didn't run or doesn't exist; ignore.
}

// 2. SAFELY GET PDF TEXT (NCR & DUMAGUETE)
let ncrPdfText = "";
let dumaPdfText = "";

try {
  const ncrNode = $('Extract NCR PDF').first();
  if (ncrNode && ncrNode.json) {
    ncrPdfText = ncrNode.json.text || ncrNode.json.data || "NCR PDF extracted but empty.";
  }
} catch (error) { }

try {
  const dumaNode = $('Extract Dumaguete PDF').first();
  if (dumaNode && dumaNode.json) {
    dumaPdfText = dumaNode.json.text || dumaNode.json.data || "Dumaguete PDF extracted but empty.";
  }
} catch (error) { }

// Combine them
pdfText = `--- NCR (Metro Manila) ---\n${ncrPdfText}\n\n--- DUMAGUETE (Visayas) ---\n${dumaPdfText}`;

// 3. SAFELY GET ACCUWEATHER
try {
  const accuNode = $('Scrape AccuWeather').first();
  if (accuNode && accuNode.json) {
    // If it's the raw HTML fallback, we just pass a snippet of the HTML body
    // The LLM is smart enough to find the forecast in raw HTML.
    let raw = JSON.stringify(accuNode.json);
    accuText = raw.substring(0, 15000); // Limit context size
  }
} catch (error) { }


const today = new Date().toLocaleDateString("en-US", {
  year: 'numeric', month: 'long', day: 'numeric'
});

// Construct the Final Source Text
const sourceText = `
[PAGASA PUBLIC FORECAST (Source 1)]
${pagasaText.substring(0, 10000)}

[ACCUWEATHER RAW DATA (Source 2)]
${accuText}

[5-DAY OUTLOOK PDF (Source 3)]
${pdfText.substring(0, 10000)}
`;

// Valid JSON Schema for the Prompt
const jsonStructure = `{
  "summary_of_current_conditions": {
    "date": "${today}",
    "system_in_effect": "",
    "metro_manila_detailed": "",
    "dumaguete_detailed": "",
    "metro_manila_email": "",
    "dumaguete_email": ""
  },
  "active_pagasa_advisories": {
    "rainfall_warning": {
      "metro_manila": { "title": "", "summary": "" }
      ,
      "dumaguete": { "title": "", "summary": "" }
    },
    "thunderstorm_warning": {
      "metro_manila": { "title": "", "summary": "" }
      ,
      "dumaguete": { "title": "", "summary": "" }
    },
    "other_advisories": [] 
  },
  "forecast_10day": {
    "accuweather": {
      "metro_manila": [],
      "dumaguete": []
    }
  },
  "site_impact_summary": {
    "metro_manila": { "impact_level": "", "justification": "" }
    ,
    "dumaguete": { "impact_level": "", "justification": "" }
  },
  "operational_status": {
    "metro_manila": "",
    "dumaguete": ""
  },
  "operational_recommendations": {
    "metro_manila": [],
    "dumaguete": []
  },
  "key_takeaways": []
}`;

// Final System Prompt
// Returning an ARRAY of OBJECTS is required by n8n
return [{
  json: {
    system_prompt: `You are generating a DAILY OPERATIONAL WEATHER SUMMARY.
OUTPUT MUST MATCH THIS JSON STRUCTURE EXACTLY.
${jsonStructure}

IMPORTANT:
1. Use the [PAGASA PUBLIC FORECAST] for the detailed outlook.
2. Check for Low Pressure Areas (LPA) or Cyclones.
3. Use [ACCUWEATHER] for the 10-day forecast.
`,
    user_message: sourceText
  }
}];
