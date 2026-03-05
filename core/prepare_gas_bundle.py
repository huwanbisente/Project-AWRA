
import base64
import os
import re
from pathlib import Path

def get_base64_image(path):
    if not os.path.exists(path):
        print(f"Warning: {path} not found")
        return ""
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def bundle_html(template_path, output_path, logo_b64=None, pagasa_b64=None):
    if not os.path.exists(template_path):
        print(f"Skipping: {template_path} (not found)")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Base64 Encode Assets if found in HTML
    if logo_b64:
        html = html.replace('src="assets/ece_logo_cropped.png"', f'src="data:image/png;base64,{logo_b64}"')
    if pagasa_b64:
        html = html.replace('src="assets/pagasa_logo.png"', f'src="data:image/png;base64,{pagasa_b64}"')

    # 2. Modify script for GAS compatibility
    gas_init_js = """
function init() {
    if (typeof google === 'undefined') {
        console.warn("GAS Environment not detected.");
        return;
    }
    google.script.run
        .withSuccessHandler(function(jsonString) {
            try {
                const data = JSON.parse(jsonString);
                globalData = data;
                
                document.getElementById('last-updated').innerText = data.summary_of_current_conditions?.date?.toUpperCase() || "--";
                document.getElementById('ticker-text').innerText = (data.summary_of_current_conditions?.system_in_effect || "SYNC NORMAL").toUpperCase();

                // Dynamic UI components
                const mData = data.forecast_10day?.accuweather?.metro_manila?.[0];
                const dData = data.forecast_10day?.accuweather?.dumaguete?.[0];

                if (mData && document.getElementById('mnl-temp-range')) {
                    document.getElementById('mnl-temp-range').innerText = `${mData.min_temp}° / ${mData.max_temp}°`;
                    document.getElementById('mnl-rain-prob').innerHTML = `<i class="fa-solid fa-droplet"></i> ${mData.pop}%`;
                }
                if (dData && document.getElementById('dgt-temp-range')) {
                    document.getElementById('dgt-temp-range').innerText = `${dData.min_temp}° / ${dData.max_temp}°`;
                    document.getElementById('dgt-rain-prob').innerHTML = `<i class="fa-solid fa-droplet"></i> ${dData.pop}%`;
                }

                const highLightStorm = (txt) => {
                    if (!txt) return "";
                    let formatted = txt;
                    const keywords = ["Tropical Depression", "Tropical Storm", "Severe Tropical Storm", "Typhoon", "Super Typhoon", "Cyclone"];
                    keywords.forEach(word => {
                        const regex = new RegExp(word, 'gi');
                        formatted = formatted.replace(regex, (match) => `<span class="text-red-600 font-black">${match}</span>`);
                    });
                    formatted = formatted.replace(/\\(([^)]+)\\)/g, '<span class="text-red-600 font-black">($1)</span>');
                    return formatted;
                };
                
                const sysEffect = (data.summary_of_current_conditions?.system_in_effect || "").toLowerCase();
                const isActive = sysEffect.includes("storm") || sysEffect.includes("typhoon") || sysEffect.includes("cyclone");
                
                const monTxt = document.getElementById('typhoon-text');
                if (monTxt) {
                    if (isActive) {
                        monTxt.innerHTML = highLightStorm(data.summary_of_current_conditions.system_in_effect);
                        monTxt.className = "text-[11px] font-bold text-slate-800 leading-tight";
                    } else {
                        monTxt.innerText = "NO SYSTEMS IN PAR";
                    }
                }

                if (document.getElementById('takeaways-list')) {
                    document.getElementById('takeaways-list').innerHTML = (data.key_takeaways || []).map(t => `<li class="flex gap-4 items-start"><i class="fa-solid fa-check-circle text-emerald-500 mt-0.5 shrink-0 text-[11px]"></i><span class="text-[11px] text-slate-500 font-medium leading-tight tracking-tight line-clamp-2">${t}</span></li>`).join('');
                }

                renderForecast('Manila');
            } catch (e) { console.error("Parse Error", e); }
        })
        .getData();
}
"""
    
    # Replace the existing script or init call
    if '<script>' in html:
        # If it has the old init, replace it. If not, just append it before </body>
        pattern = r'async function init\(\) \{.*?init\(\);'
        if re.search(pattern, html, flags=re.DOTALL):
            html = re.sub(pattern, gas_init_js + "\ninit();", html, flags=re.DOTALL)
        else:
            # For templates like Remedy that might have a different JS structure
            html = html.replace('</body>', f'<script>\n{gas_init_js}\ninit();\n</script>\n</body>')

    # 3. Direct Link Fixes
    pdf_link = "https://drive.google.com/file/d/1wMF4WO1QdjlKwTSJ_uyLF6T5ahCQaS9b/view"
    html = html.replace('href="weather_report.pdf"', f'href="{pdf_link}"')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {output_path}")

def main():
    root = Path("f:/for PORTFOLIO/ECE_Project_AWRA")
    webapp_dir = root / "webapp"
    
    # Load Image Data once
    ece_logo = get_base64_image(webapp_dir / "assets" / "ece_logo_cropped.png")
    pagasa_logo = get_base64_image(webapp_dir / "assets" / "pagasa_logo.png")

    # 1. Project AWRA (Main)
    bundle_html(
        template_path=webapp_dir / "templates" / "source_AWRA.html",
        output_path=webapp_dir / "index_AWRA.html",
        logo_b64=ece_logo,
        pagasa_b64=pagasa_logo
    )

    # 2. Remedy Dashboard (New Account)
    bundle_html(
        template_path=webapp_dir / "templates" / "source_REMEDY.html",
        output_path=webapp_dir / "index_REMEDY.html",
        logo_b64=None, # Remedy uses CSS logo
        pagasa_b64=pagasa_logo
    )

if __name__ == "__main__":
    main()
