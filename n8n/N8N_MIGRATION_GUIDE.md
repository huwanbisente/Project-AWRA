# n8n Migration Guide: Project AWRA

This guide explains how to import and configure the Native n8n Workflow.

## 1. Import the Workflow
1.  Open your n8n Dashboard.
2.  Click **"Add Workflow"** -> **"Import from..."**.
3.  Upload or paste the content of `n8n_workflow_spec.json`.

## 2. Configure Credentials
You must set up the following credentials in n8n:
*   **OpenAI API**: Add your API Key.
*   **Puppeteer / Browserless**:
    *   If using the **Puppeteer Node (Community)**: Ensure it is installed (`npm install n8n-nodes-puppeteer` in your n8n custom directory).
    *   If using **Browserless**: Update the "Scrape PAGASA" node to use an HTTP Request to your Browserless endpoint.

## 3. Update JavaScript Logic
The `Aggregator & Prompt Prep` node in the JSON is a placeholder. You must:
1.  Open `n8n_javascript_parsers.js`.
2.  Copy the code from **PART 3**.
3.  Paste it into the **Code** field of the "Aggregator & Prompt Prep" node in n8n.

## 4. Verify Nodes
*   **Webhook**: Ensure the method is `GET` and path is `weather-report`.
*   **PDF Download**: Check that the URL is correct (`https://pubfiles.pagasa.dost.gov.ph/...`).
*   **OpenAI**: Ensure the Model ID (`gpt-4` or `gpt-3.5-turbo`) matches your plan.

## 5. Test
1.  Click **"Execute Workflow"**.
2.  Check the output of the **"Respond to Webhook"** node.
3.  It should return the full `summary.json` structure.
