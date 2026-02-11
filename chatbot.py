# --- RECIPE DATABASE (With Multi-Language Support) ---
RECIPE_DB = {
    "Diabetes": [
        {"name": {"English": "Diabetic-Friendly Chicken Curry", "Hindi": "डायबिटिक चिकन करी", "Tamil": "நீரிழிவு நோய் கோழி குழம்பு"}, 
         "url": "https://www.diabetesfoodhub.org/recipes/chicken-curry.html", "type": "main"},
        {"name": {"English": "Low-Carb Spinach Dal", "Hindi": "पालक दाल (कम कार्ब)", "Tamil": "கீரை பருப்பு"}, 
         "url": "https://www.vegrecipesofindia.com/palak-dal-recipe/", "type": "main"},
        {"name": {"English": "Quinoa Upma", "Hindi": "क्विनोआ उपमा", "Tamil": "குயினோவா உப்புமா"}, 
         "url": "https://www.indianhealthyrecipes.com/quinoa-upma-recipe/", "type": "breakfast"},
        {"name": {"English": "Bitter Gourd Stir Fry", "Hindi": "करेला फ्राई", "Tamil": "பாகற்காய் வறுவல்"}, 
         "url": "https://www.indianhealthyrecipes.com/bitter-gourd-fry-recipe/", "type": "side"}
    ],
    "Hypertension": [
        {"name": {"English": "DASH Diet Vegetable Stir-Fry", "Hindi": "सब्जी फ्राई (DASH)", "Tamil": "காய்கறி பொரியல்"}, 
         "url": "https://www.mayoclinic.org/healthy-lifestyle/recipes/veggie-stir-fry/rcp-20049965", "type": "main"},
        {"name": {"English": "Low-Sodium Roti", "Hindi": "कम नमक वाली रोटी", "Tamil": "உப்பு இல்லாத சப்பாத்தி"}, 
         "url": "https://www.tarladalal.com/low-salt-roti-33092r", "type": "main"}
    ],
    "High Cholesterol": [
        {"name": {"English": "Oats Idli", "Hindi": "ओट्स इडली", "Tamil": "ஓட்ஸ் இட்லி"}, 
         "url": "https://www.indianhealthyrecipes.com/oats-idli-recipe/", "type": "breakfast"},
        {"name": {"English": "Grilled Fish", "Hindi": "ग्रिल्ड फिश", "Tamil": "மீன் வறுவல் (எண்ணெய் இல்லாத)"}, 
         "url": "https://www.eatingwell.com/recipe/252562/grilled-fish-with-lemon/", "type": "main"}
    ],
    "General": [
        {"name": {"English": "Mixed Vegetable Soup", "Hindi": "मिक्स वेज सूप", "Tamil": "காய்கறி சூப்"}, 
         "url": "https://www.vegrecipesofindia.com/mix-vegetable-soup-recipe/", "type": "side"},
        {"name": {"English": "Fruit Salad", "Hindi": "फ्रूट सलाद", "Tamil": "பழ கலவை"}, 
         "url": "https://www.indianhealthyrecipes.com/fruit-salad-recipe/", "type": "breakfast"}
    ]
}

# --- CHATBOT TRANSLATIONS ---
CHAT_TRANS = {
    "English": {
        "greeting": "👋 Hello! I am your AI Nutrition Assistant. Ask me for recipes like 'breakfast ideas'.",
        "intro": "👨‍🍳 **Based on your condition ({}), here are my suggestions:**",
        "fallback": "I didn't quite catch that. Try asking for 'breakfast' or 'lunch'.",
        "general_fallback": "I couldn't find specific recipes, but try these general healthy options:",
        "friendly": "Friendly"
    },
    "Hindi": {
        "greeting": "👋 नमस्ते! मैं आपका एआई पोषण सहायक हूं। मुझसे 'नाश्ते के विचार' जैसी रेसिपी पूछें।",
        "intro": "👨‍🍳 **आपकी स्थिति ({}) के आधार पर, यहाँ मेरे सुझाव हैं:**",
        "fallback": "मुझे समझ नहीं आया। 'नाश्ता' या 'दोपहर का भोजन' के लिए पूछें।",
        "general_fallback": "मुझे विशिष्ट रेसिपी नहीं मिली, लेकिन ये सामान्य स्वस्थ विकल्प आज़माएं:",
        "friendly": "के अनुकूल"
    },
    "Tamil": {
        "greeting": "👋 வணக்கம்! நான் உங்கள் AI ஊட்டச்சத்து உதவியாளர். 'காலை உணவு' போன்ற சமையல் குறிப்புகளை என்னிடம் கேளுங்கள்.",
        "intro": "👨‍🍳 **உங்கள் உடல்நிலை ({}) அடிப்படையில், இதோ எனது பரிந்துரைகள்:**",
        "fallback": "எனக்கு புரியவில்லை. 'காலை உணவு' அல்லது 'மதிய உணவு' என்று கேளுங்கள்.",
        "general_fallback": "குறிப்பிட்ட சமையல் குறிப்புகள் கிடைக்கவில்லை, ஆனால் இந்த ஆரோக்கியமான விருப்பங்களை முயற்சிக்கவும்:",
        "friendly": "உகந்தது"
    }
}

def get_response(query, diagnosis_list, lang="English"):
    """Generates responses based on user query, health condition, and language."""
    query = query.lower()
    
    # Get translation dictionary (Default to English if lang not found)
    t = CHAT_TRANS.get(lang, CHAT_TRANS["English"])
    
    # --- 1. HANDLE GREETINGS ---
    if any(x in query for x in ["hi", "hello", "hey", "vanakkam", "namaste"]):
        return t["greeting"]
    
    # --- 2. IDENTIFY HEALTH CONDITION ---
    categories = set()
    if any("Diabetes" in d for d in diagnosis_list): categories.add("Diabetes")
    if any("Hypertension" in d for d in diagnosis_list): categories.add("Hypertension")
    if any("Cholesterol" in d for d in diagnosis_list): categories.add("High Cholesterol")
    if not categories: categories.add("General")

    # --- 3. FILTER & BUILD RESPONSE ---
    food_keywords = ["recipe", "food", "eat", "breakfast", "lunch", "dinner", "snack", "diet", "meal", "unavu", "khana"]
    if any(k in query for k in food_keywords):
        
        # Display categories in local language? Keeping medical terms in English for now.
        cat_str = ", ".join(categories)
        response_lines = [t["intro"].format(cat_str)]
        
        filter_type = None
        if "breakfast" in query or "kalai" in query or "nashta" in query: filter_type = "breakfast"
        elif "lunch" in query or "dinner" in query or "mathiyam" in query: filter_type = "main"
        elif "snack" in query: filter_type = "side"

        found = False
        for cat in categories:
            recipes = RECIPE_DB.get(cat, []) + RECIPE_DB.get("General", [])
            for r in recipes:
                if filter_type and r["type"] != filter_type:
                    continue
                
                # Get Recipe Name in Language
                r_name = r["name"].get(lang, r["name"]["English"])
                
                response_lines.append(f"🔗 [{r_name}]({r['url']})")
                found = True
        
        if not found:
            response_lines.append(t["general_fallback"])
            for r in RECIPE_DB["General"]:
                 r_name = r["name"].get(lang, r["name"]["English"])
                 response_lines.append(f"🔗 [{r_name}]({r['url']})")
                 
        return "\n\n".join(list(set(response_lines)))

    return t["fallback"]