// ------------------------------------------------------------------
// PART 1: PARSE PAGASA TEXT (From HTML Extract Node)
// ------------------------------------------------------------------
// Input: items[0].json.data (extracted text from body)
const rawText = items[0].json.data || "";

const cleanedText = rawText
    .replace("Skip to main content", "")
    .replace("Toggle navigation", "")
    .trim();

// ------------------------------------------------------------------
// PART 3: AGGREGATE & PREPARE PROMPT (Master Aggregator)
// ------------------------------------------------------------------
let pagasaText = "No PAGASA data available.";
let accuManila = "No AccuWeather Manila data.";
let accuDuma = "No AccuWeather Dumaguete data.";
let pdfText = "No PDF data available.";
let ncrWarnings = "";
let dumaWarnings = "";

// 1. PAGASA TEXT
try {
    const pagasaNode = $('Extract PAGASA Text').first();
    if (pagasaNode && pagasaNode.json) {
        pagasaText = pagasaNode.json.data || "";
    }
} catch (e) { }

// 2. NCR DATA (PDF + Warnings)
let ncrPdfText = "";
try {
    const pdfNode = $('Extract NCR PDF').first();
    if (pdfNode && pdfNode.json) ncrPdfText = pdfNode.json.text || "";
} catch (e) { }

try {
    // We extracted these in 'Extract NCR Page Data'
    const pageNode = $('Extract NCR Page Data').first();
    if (pageNode && pageNode.json) {
        let r = pageNode.json.rainfall || "No Rainfall Warning";
        let t = pageNode.json.thunderstorm || "No Thunderstorm Warning";
        ncrWarnings = `RAIN: ${r}\nTHUNDER: ${t}`;
    }
} catch (e) { }

// 3. DUMAGUETE DATA (PDF + Warnings)
let dumaPdfText = "";
try {
    const pdfNode = $('Extract Dumaguete PDF').first();
    if (pdfNode && pdfNode.json) dumaPdfText = pdfNode.json.text || "";
} catch (e) { }

try {
    const pageNode = $('Extract Dumaguete Page Data').first();
    if (pageNode && pageNode.json) {
        let r = pageNode.json.rainfall || "No Rainfall Warning";
        let t = pageNode.json.thunderstorm || "No Thunderstorm Warning";
        dumaWarnings = `RAIN: ${r}\nTHUNDER: ${t}`;
    }
} catch (e) { }

// 4. ACCUWEATHER
try {
    const node = $('Scrape AccuWeather Manila').first();
    if (node && node.json) accuManila = JSON.stringify(node.json).substring(0, 10000);
} catch (e) { }

try {
    const node = $('Scrape AccuWeather Dumaguete').first();
    if (node && node.json) accuDuma = JSON.stringify(node.json).substring(0, 10000);
} catch (e) { }


const sourceText = `
[PAGASA PUBLIC FORECAST]
${pagasaText.substring(0, 8000)}

[NCR REGIONAL (Metro Manila)]
Warnings:
${ncrWarnings}
PDF Outlook:
${ncrPdfText.substring(0, 5000)}

[VISAYAS REGIONAL (Dumaguete)]
Warnings:
${dumaWarnings}
PDF Outlook:
${dumaPdfText.substring(0, 5000)}

[ACCUWEATHER MANILA]
${accuManila}

[ACCUWEATHER DUMAGUETE]
${accuDuma}
`;

const today = new Date().toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric' });

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
      "metro_manila": { "title": "", "summary": "" },
      "dumaguete": { "title": "", "summary": "" }
    },
    "thunderstorm_warning": {
      "metro_manila": { "title": "", "summary": "" },
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
    "metro_manila": { "impact_level": "", "justification": "" },
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

return [{
    json: {
        system_prompt: `You are generating a DAILY OPERATIONAL WEATHER SUMMARY.
OUTPUT MUST MATCH THIS JSON STRUCTURE EXACTLY.
${jsonStructure}

IMPORTANT:
1. Use [PAGASA PUBLIC FORECAST] and [REGIONAL] sections for official data.
2. Check [NCR REGIONAL] and [VISAYAS REGIONAL] for Rainfall/Thunderstorm warnings.
3. Use [ACCUWEATHER] sources for the 10-day forecast table only.
`,
        user_message: sourceText
    }
}];
