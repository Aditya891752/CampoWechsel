"""
Bilingual Internationalization (i18n) Engine for Field Shift.
Provides seamless English and Hindi interface localization.
"""

TRANSLATIONS = {
    "en": {
        "title": "Field Shift: Western Kansas",
        "subtitle": "Farmer-Friendly Crop-Rotation Decision Support with NASA Earth Observations",
        "advisory": (
            "Important Advisory: This tool highlights satellite-detected patterns and agronomic alternatives. "
            "It supports farmer judgment and never replaces the on-the-ground experience of producers, certified crop advisers (CCAs), "
            "or Kansas State University Extension specialists."
        ),
        "farm_setup": "Farm Location & Persona",
        "select_county": "Select County & Agricultural System",
        "priority_sliders": "Farmer Priority Sliders",
        "priority_caption": "Adjust what matters most on your operation (0 to 10 scale):",
        "save_water": "1. Save Water (Efficiency / Aquifer Protection)",
        "protect_soil": "2. Protect Soil (Residue / Wind Erosion Defense)",
        "earn_income": "3. Earn Income (Margin Reliability / Input Cost)",
        "climate_scenarios": "Climate Scenarios (P1)",
        "climate_caption": "Test how rotation rankings shift under hotter or drier conditions:",
        "rain_change": "Rainfall Change (%)",
        "temp_increase": "Temperature Increase (°C)",
        "sec_my_fields": "1. My Fields Now: Vegetation & Bare-Ground Timeline",
        "threshold_label": "Bare-Field NDVI Threshold",
        "sec_conditions": "2. Field Conditions & Stress Indicators",
        "sec_strategies": "3. Compare Crop-Rotation Strategies",
        "sec_comparison": "4. Side-by-Side Comparison: Current Practice vs. Alternative",
        "sec_timeline": "5. Annual Crop Year Timeline View",
        "sec_map": "6. Interactive Geospatial Map: Spatial Variation & Vulnerability Grid",
        "sec_groundwater": "7. Groundwater Trends & NASA GRACE-FO Hydrological Context",
        "sec_openet": "8. OpenET Crop Water Demand & Irrigation Budget",
        "sec_lst": "9. ECOSTRESS & MODIS Thermal Hotspot Analysis",
        "sec_provenance": "10. Data Provenance & Scientific Transparency",
        "download_report_btn": "Download Executive Strategy Report (HTML / Printable PDF)",
        "current_practice": "CURRENT PRACTICE",
        "rank": "RANK",
    },
    "hi": {
        "title": "फ़ील्ड शिफ्ट: पश्चिमी कंसास",
        "subtitle": "नासा पृथ्वी अवलोकन डेटा आधारित किसान-अनुकूल फसल-चक्र निर्णय सहायता",
        "advisory": (
            "महत्वपूर्ण सूचना: यह उपकरण उपग्रह-आधारित पैटर्न और कृषि विकल्पों को प्रदर्शित करता है। "
            "यह किसानों के निर्णय में सहायता करता है और स्थानीय कृषि विशेषज्ञों, प्रमाणित फसल सलाहकारों (CCA) "
            "या कंसास स्टेट यूनिवर्सिटी एक्सटेंशन विशेषज्ञों के अनुभव का स्थान कभी नहीं लेता।"
        ),
        "farm_setup": "खेत का स्थान और किसान प्रोफ़ाइल",
        "select_county": "काउंटी और कृषि प्रणाली चुनें",
        "priority_sliders": "किसान प्राथमिकता स्लाइडर्स",
        "priority_caption": "अपनी प्राथमिकताओं को अनुकूलित करें (0 से 10 पैमाना):",
        "save_water": "१. जल संरक्षण (दक्षता / भूजल सुरक्षा)",
        "protect_soil": "२. मृदा संरक्षण (हवा कटाव से सुरक्षा)",
        "earn_income": "३. आय अर्जन (विश्वसनीय लाभ / कम लागत)",
        "climate_scenarios": "जलवायु परिदृश्य सिमुलेशन (P1)",
        "climate_caption": "अधिक गर्म या सूखे मौसम में फसल चक्र रैंकिंग में परिवर्तन देखें:",
        "rain_change": "वर्षा में परिवर्तन (%)",
        "temp_increase": "तापमान में वृद्धि (°C)",
        "sec_my_fields": "१. मेरे खेत वर्तमान में: वनस्पति और बंजर भूमि समयरेखा",
        "threshold_label": "बंजर खेत एनडीवीआई (NDVI) थ्रेशोल्ड",
        "sec_conditions": "२. खेत की स्थितियाँ और पर्यावरणीय तनाव संकेतक",
        "sec_strategies": "३. फसल-चक्र रणनीतियों की तुलना करें",
        "sec_comparison": "४. आमने-सामने तुलना: वर्तमान प्रणाली बनाम नया विकल्प",
        "sec_timeline": "५. वार्षिक फसल वर्ष समयरेखा दृश्य",
        "sec_map": "६. इंटरैक्टिव भू-स्थानिक मानचित्र: भेद्यता ग्रिड",
        "sec_groundwater": "७. ओगालाला जलभृत रुझान और नासा ग्रेस-एफओ (GRACE-FO)",
        "sec_openet": "८. ओपन-ईटी (OpenET) फसल जल मांग और सिंचाई बजट",
        "sec_lst": "९. इकोस्ट्रेस और थर्मल हॉटस्पॉट विश्लेषण",
        "sec_provenance": "१०. डेटा स्रोत और वैज्ञानिक पारदर्शिता",
        "download_report_btn": "कार्यकारी रणनीति रिपोर्ट डाउनलोड करें (प्रिंट करने योग्य PDF / HTML)",
        "current_practice": "वर्तमान अभ्यास",
        "rank": "रैंक",
    },
}


def get_text(key: str, lang: str = "en") -> str:
    """Retrieve translated string with fallback to English."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
