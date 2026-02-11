import sqlite3
import pandas as pd
import datetime
import hashlib
import os

DB_NAME = "hospital.db"
CSV_FILE = "patient_data.csv"

# --- INGREDIENT TRANSLATIONS ---
INGREDIENT_TRANSLATIONS = {
    # AVOID ITEMS
    "White Rice": {"Hindi": "सफेद चावल", "Tamil": "வெள்ளை அரிசி", "Malayalam": "വെള്ള അരി", "Telugu": "తెల్ల అన్నం"},
    "Potatoes": {"Hindi": "आलू", "Tamil": "உருளைக்கிழங்கு", "Malayalam": "ഉരുളക്കിഴങ്ങ്", "Telugu": "బంగాళాదుంప"},
    "White Bread": {"Hindi": "सफेद ब्रेड", "Tamil": "வெள்ளை ரொட்டி", "Malayalam": "വെള്ള ബ്രെഡ്", "Telugu": "వైట్ బ్రెడ్"},
    "Sugary Drinks": {"Hindi": "मीठे पेय", "Tamil": "சர்க்கரை பானங்கள்", "Malayalam": "മധുര പാനീയങ്ങൾ", "Telugu": "చక్కెర పానీయాలు"},
    "Cakes": {"Hindi": "केक", "Tamil": "கேக்குகள்", "Malayalam": "കേക്കുകൾ", "Telugu": "కేకులు"},
    "Processed Snacks": {"Hindi": "प्रोसेस्ड स्नैक्स", "Tamil": "பதப்படுத்தப்பட்ட தின்பண்டங்கள்", "Malayalam": "സംസ്കരിച്ച ലഘുഭക്ഷണങ്ങൾ", "Telugu": "ప్రాసెస్ చేసిన స్నాక్స్"},
    "Ice Cream": {"Hindi": "आइसक्रीम", "Tamil": "ஐஸ்கிரீம்", "Malayalam": "ഐസ് ക്രീം", "Telugu": "ఐస్ క్రీం"},
    "Red Meat": {"Hindi": "लाल मांस", "Tamil": "சிவப்பு இறைச்சி", "Malayalam": "ചുവന്ന മാംസം", "Telugu": "ఎర్ర మాంసం"},
    "Cheese": {"Hindi": "पनीर", "Tamil": "பாலாடைக்கட்டி (Cheese)", "Malayalam": "ചീസ്", "Telugu": "జున్ను (Cheese)"},
    "Fried Foods": {"Hindi": "तला हुआ भोजन", "Tamil": "வறுத்த உணவுகள்", "Malayalam": "വറുത്ത ഭക്ഷണങ്ങൾ", "Telugu": "వేయించిన ఆహారాలు"},
    "Butter": {"Hindi": "मक्खन", "Tamil": "வெண்ணெய்", "Malayalam": "വെണ്ണ", "Telugu": "వెన్న"},
    "Palm Oil": {"Hindi": "ताड़ का तेल", "Tamil": "பாமாயில்", "Malayalam": "പാം ഓയിൽ", "Telugu": "పామాయిల్"},
    "Egg Yolks": {"Hindi": "अंडे की जर्दी", "Tamil": "முட்டையின் மஞ்சள் கரு", "Malayalam": "മുട്ടയുടെ മഞ്ഞക്കരു", "Telugu": "గుడ్డు సొన"},
    "Pickles": {"Hindi": "अचार", "Tamil": "ஊறுகாய்", "Malayalam": "അച്ചാർ", "Telugu": "పచ్చడి"},
    "Papad": {"Hindi": "पापड़", "Tamil": "அப்பளம்", "Malayalam": "പപ്പടം", "Telugu": "అప్పడం"},
    "Salted Nuts": {"Hindi": "नमकीन मेवे", "Tamil": "உப்பு கலந்த பருப்புகள்", "Malayalam": "ഉപ്പിലിട്ട അണ്ടിപ്പരിപ്പ്", "Telugu": "ఉప్పు వేసిన గింజలు"},
    "Canned Soups": {"Hindi": "डिब्बाबंद सूप", "Tamil": "டின்களில் அடைக்கப்பட்ட சூப்கள்", "Malayalam": "ടിന്നിലടച്ച സൂപ്പ്", "Telugu": "క్యాన్డ్ సూప్స్"},
    "Processed Meats": {"Hindi": "प्रोसेस्ड मीट", "Tamil": "பதப்படுத்தப்பட்ட இறைச்சி", "Malayalam": "സംസ്കരിച്ച മാംസം", "Telugu": "ప్రాసెస్ చేసిన మాంసం"},
    "Excess Salt": {"Hindi": "अधिक नमक", "Tamil": "அதிக உப்பு", "Malayalam": "അമിതമായ ഉപ്പ്", "Telugu": "అధిక ఉప్పు"},
    "High Calorie Snacks": {"Hindi": "हाई कैलोरी स्नैक्स", "Tamil": "அதிக கலோரி தின்பண்டங்கள்", "Malayalam": "ഉയർന്ന കലോറി ലഘുഭക്ഷണങ്ങൾ", "Telugu": "అధిక కేలరీల స్నాక్స్"},
    "Fast Food": {"Hindi": "फास्ट फूड", "Tamil": "துரித உணவு", "Malayalam": "ഫാസ്റ്റ് ഫുഡ്", "Telugu": "ఫాస్ట్ ఫుడ్"},
    "Tea/Coffee with meals": {"Hindi": "खाने के साथ चाय/कॉफी", "Tamil": "உணவுடன் தேநீர்/காபி", "Malayalam": "ഭക്ഷണത്തോടൊപ്പം ചായ/കാപ്പി", "Telugu": "భోజనంతో టీ/కాఫీ"},
    
    # BOOST ITEMS
    "Bitter Gourd": {"Hindi": "करेला", "Tamil": "பாகற்காய்", "Malayalam": "പാവയ്ക്ക", "Telugu": "కాకరకాయ"},
    "Fenugreek": {"Hindi": "मेथी", "Tamil": "வெந்தயம்", "Malayalam": "ഉലുവ", "Telugu": "మెంతులు"},
    "Barley": {"Hindi": "जौ", "Tamil": "பार्லி", "Malayalam": "ബാർലി", "Telugu": "బార్లీ"},
    "Jamun": {"Hindi": "जामुन", "Tamil": "நாவல் பழம்", "Malayalam": "ഞാവൽ പഴം", "Telugu": "నేరేడు పండు"},
    "Spinach": {"Hindi": "पालक", "Tamil": "கீரை", "Malayalam": "ചീര", "Telugu": "పాలకూర"},
    "Whole Grains": {"Hindi": "साबुत अनाज", "Tamil": "முழு தானியங்கள்", "Malayalam": "ധാന്യങ്ങൾ", "Telugu": "తృణధాన్యాలు"},
    "Legumes": {"Hindi": "फलियां", "Tamil": "பருப்பு வகைகள்", "Malayalam": "പയർവർഗ്ഗങ്ങൾ", "Telugu": "పప్పుధాన్యాలు"},
    "Quinoa": {"Hindi": "क्विनोआ", "Tamil": "குயினோவா", "Malayalam": "ക്വിinoa", "Telugu": "క్వినోవా"},
    "Oats": {"Hindi": "ओट्स", "Tamil": "ஓட்ஸ்", "Malayalam": "ഓട്സ്", "Telugu": "ఓట్స్"},
    "Garlic": {"Hindi": "लहसुन", "Tamil": "பூண்டு", "Malayalam": "വെളുത്തുള്ളി", "Telugu": "వెల్లుల్లి"},
    "Walnuts": {"Hindi": "अखरोट", "Tamil": "வால்நட்", "Malayalam": "വാൽനട്ട്", "Telugu": "వాల్ నట్స్"},
    "Almonds": {"Hindi": "बादाम", "Tamil": "பாதாம்", "Malayalam": "ബദാം", "Telugu": "బాదం"},
    "Avocados": {"Hindi": "एवोकैडो", "Tamil": "அவகேடோ", "Malayalam": "അവക്കാഡോ", "Telugu": "అవకాడో"},
    "Fatty Fish (Salmon)": {"Hindi": "फैटी फिश (सैल्मन)", "Tamil": "மீன் (சால்மன்)", "Malayalam": "കൊഴുപ്പുള്ള മത്സ്യം", "Telugu": "కొవ్వు చేపలు"},
    "Olive Oil": {"Hindi": "जैतून का तेल", "Tamil": "ஆலிவ் எண்ணெய்", "Malayalam": "ഒലിവ് ഓയിൽ", "Telugu": "ఆలివ్ నూనె"},
    "Bananas": {"Hindi": "केला", "Tamil": "வாழைப்பழம்", "Malayalam": "പഴം", "Telugu": "అరటిపండు"},
    "Beetroot": {"Hindi": "चुकंदर", "Tamil": "பீட்ரூட்", "Malayalam": "ബീറ്റ്റൂട്ട്", "Telugu": "బీట్‌రూట్"},
    "Watermelon": {"Hindi": "तरबूज", "Tamil": "தர்பூசணி", "Malayalam": "തണ്ണിമത്തൻ", "Telugu": "పుచ్చకాయ"},
    "Curd": {"Hindi": "दही", "Tamil": "தயிர்", "Malayalam": "തൈര്", "Telugu": "పెరుగు"},
    "Coconut Water": {"Hindi": "नारियल पानी", "Tamil": "இளநீர்", "Malayalam": "കരിക്ക്", "Telugu": "కొబ్బరి నీళ్ళు"},
    "Dates": {"Hindi": "खजूर", "Tamil": "பேரிச்சம்பழம்", "Malayalam": "ഈത്തപ്പഴം", "Telugu": "ఖర్జూరం"},
    "Pomegranate": {"Hindi": "अनार", "Tamil": "மாதுளை", "Malayalam": "മാതളനാരങ്ങ", "Telugu": "దానిమ్మ"},
    "Drumstick Leaves": {"Hindi": "सहजन के पत्ते", "Tamil": "முருங்கை கீரை", "Malayalam": "മുരിങ്ങ ഇല", "Telugu": "మునగాకు"},
    "Jaggery": {"Hindi": "गुड़", "Tamil": "வெல்லம்", "Malayalam": "ശർക്കര", "Telugu": "బెల్లం"},
    "High Fiber Veggies": {"Hindi": "हाई फाइबर सब्जियां", "Tamil": "நார்ச்சத்து உள்ள காய்கறிகள்", "Malayalam": "നാരുകൾ അടങ്ങിയ പച്ചക്കറികൾ", "Telugu": "పీచు పదార్థాలు ఉన్న కూరగాయలు"},
    "Water": {"Hindi": "पानी", "Tamil": "தண்ணீர்", "Malayalam": "വെള്ളം", "Telugu": "నీరు"},
    "Cucumber": {"Hindi": "खीरा", "Tamil": "வெள்ளரிக்காய்", "Malayalam": "വെള്ളരിക്ക", "Telugu": "దోసకాయ"},
    "Melons": {"Hindi": "खरबूजे", "Tamil": "முலாம்பழம்", "Malayalam": "മത്തങ്ങ", "Telugu": "కర్బూజా"},
    "Broccoli": {"Hindi": "ब्रोकोली", "Tamil": "ப்ரோக்கோலி", "Malayalam": "ബ്രോക്കോളി", "Telugu": "బ్రోకలీ"},
    "Nuts": {"Hindi": "मेवे", "Tamil": "பருப்புகள்", "Malayalam": "നട്സ്", "Telugu": "గింజలు"},
    "Dairy": {"Hindi": "दुग्धालय", "Tamil": "பால் பொருட்கள்", "Malayalam": "പാലുൽപ്പന്നങ്ങൾ", "Telugu": "పాల ఉత్పత్తులు"},
    "Protein Shakes": {"Hindi": "प्रोटीन शेक", "Tamil": "புரத சத்து பானம்", "Malayalam": "പ്രോട്ടീൻ ഷേക്കുകൾ", "Telugu": "ప్రోటీన్ షేక్స్"},
    "Peanut Butter": {"Hindi": "पीनट बटर", "Tamil": "கடலை வெண்ணெய்", "Malayalam": "കടല വെണ്ണ", "Telugu": "వేరుశెనగ వెన్న"},
    "Ghee": {"Hindi": "घी", "Tamil": "நெய்", "Malayalam": "നെയ്യ്", "Telugu": "నెయ్యి"}
}

# --- TRANSLATIONS (Native Scripts for UI & PDF) ---
TRANSLATIONS = {
    "English": {
        "Header": "Nutrition & Health Report", "Hospital": "Smart Care Hospital",
        "Patient": "Patient Name", "Doctor": "Doctor Name", "Date": "Date",
        "Vitals_Title": "Clinical Vitals", "Sugar": "Sugar", "BP": "Blood Pressure", "BMI": "BMI", "Weight": "Weight",
        "Medicines_Title": "Prescribed Medicines", "Diagnosis_Title": "Diagnosis", "Diet_Title": "Diet Plan",
        "Avoid": "Avoid", "Eat": "Eat", "Disclaimer": "Generated by NutriScript-AI"
    },
    "Hindi": {
        "Header": "पोषण और स्वास्थ्य रिपोर्ट", "Hospital": "स्मार्ट केयर अस्पताल",
        "Patient": "रोगी का नाम", "Doctor": "डॉक्टर का नाम", "Date": "तारीख",
        "Vitals_Title": "स्वास्थ्य मापदंड", "Sugar": "शुगर", "BP": "रक्तचाप", "BMI": "बीएमआई", "Weight": "वजन",
        "Medicines_Title": "दवाइयां", "Diagnosis_Title": "निदान", "Diet_Title": "आहार योजना",
        "Avoid": "परहेज करें", "Eat": "खाएं", "Disclaimer": "न्यूट्रीस्क्रिप्ट-एआई द्वारा निर्मित"
    },
    "Tamil": {
        "Header": "சத்துணவு மற்றும் சுகாதார அறிக்கை", "Hospital": "ஸ்மார்ட் கேர் மருத்துவமனை",
        "Patient": "நோயாளி பெயர்", "Doctor": "மருத்துவர் பெயர்", "Date": "தேதி",
        "Vitals_Title": "உடல் நிலைகள்", "Sugar": "சர்க்கரை", "BP": "இரத்த அழுத்தம்", "BMI": "பிஎம்ஐ", "Weight": "எடை",
        "Medicines_Title": "மருந்துகள்", "Diagnosis_Title": "கணிப்பு", "Diet_Title": "உணவு முறை",
        "Avoid": "தவிர்க்கவும்", "Eat": "சாப்பிடவும்", "Disclaimer": "NutriScript-AI உருவாக்கியது"
    },
    "Malayalam": {
        "Header": "പോഷകാഹാര ആരോഗ്യ റിപ്പോർട്ട്", "Hospital": "സ്മാർട്ട് കെയർ ആശുപത്രി",
        "Patient": "രോഗിയുടെ പേര്", "Doctor": "ഡോക്ടറുടെ പേര്", "Date": "തീയതി",
        "Vitals_Title": "ക്ലിനിക്കൽ വൈറ്റൽസ്", "Sugar": "ഷുഗർ", "BP": "രക്തസമ്മർദ്ദം", "BMI": "ബി.എം.ഐ", "Weight": "ഭാരം",
        "Medicines_Title": "നിർദ്ദേശിച്ച മരുന്നുകൾ", "Diagnosis_Title": "രോഗനിർണയം", "Diet_Title": "ഡയറ്റ് പ്ലാൻ",
        "Avoid": "ഒഴിവാക്കേണ്ടവ", "Eat": "കഴിക്കേണ്ടവ", "Disclaimer": "NutriScript-AI തയ്യാറാക്കിയത്"
    },
    "Telugu": {
        "Header": "పోషకాహార మరియు ఆరోగ్య నివేదిక", "Hospital": "స్మార్ట్ కేర్ హాస్పిటల్",
        "Patient": "రోగి పేరు", "Doctor": "డాక్టర్ పేరు", "Date": "తేదీ",
        "Vitals_Title": "ఆరోగ్య వివరాలు", "Sugar": "షుగర్", "BP": "రక్తపోటు", "BMI": "బి.ఎం.ఐ", "Weight": "బరువు",
        "Medicines_Title": "మందులు", "Diagnosis_Title": "వ్యాధి నిర్ధారణ", "Diet_Title": "ఆహార ప్రణాళిక",
        "Avoid": "తినకూడనివి", "Eat": "తినవలసినవి", "Disclaimer": "NutriScript-AI ద్వారా రూపొందించబడింది"
    }
}

UI_TRANSLATIONS = TRANSLATIONS

def get_trans(lang, key, context='ui'):
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["English"])
    return lang_dict.get(key, key)

def get_ingredient_name(name, lang):
    """Translates an ingredient name to the target language."""
    if lang == "English": return name
    if name in INGREDIENT_TRANSLATIONS:
        return INGREDIENT_TRANSLATIONS[name].get(lang, name)
    return name

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 1. Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, 
                  full_name TEXT, id INTEGER, region TEXT, food_type TEXT, hospital_name TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (report_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, 
                  patient_name TEXT, sugar REAL, cholesterol REAL, bp INTEGER, 
                  hemoglobin REAL, height REAL, weight REAL, bmi REAL,
                  doc_id INTEGER, report_date TEXT, medicines TEXT, hospital_name TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions (prescription_id INTEGER PRIMARY KEY AUTOINCREMENT, report_id INTEGER, patient_id INTEGER, diet_plan TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (appt_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, patient_name TEXT, doc_id INTEGER, status TEXT, date_requested TEXT, admin_message TEXT)''')
    
    # NEW: Availability Table
    c.execute('''CREATE TABLE IF NOT EXISTS availability (avail_id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id INTEGER, available_date TEXT, is_booked INTEGER DEFAULT 0)''')

    # 2. AUTO-REPAIR
    try: c.execute("ALTER TABLE users ADD COLUMN hospital_name TEXT")
    except sqlite3.OperationalError: pass
    try: c.execute("ALTER TABLE reports ADD COLUMN hospital_name TEXT")
    except sqlite3.OperationalError: pass
    # Add message column if missing
    try: c.execute("ALTER TABLE appointments ADD COLUMN admin_message TEXT")
    except sqlite3.OperationalError: pass

    # 3. CREATE DEFAULT ADMIN & LOAD DATA
    create_admin_user(c)
    load_csv_dataset(c)

    conn.commit()
    conn.close()

def create_admin_user(cursor):
    """Creates a default Admin Office user."""
    default_pw = hash_password("1234")
    cursor.execute("INSERT OR REPLACE INTO users (username, password, role, full_name, id, region, food_type, hospital_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                   ("admin", default_pw, "Admin", "Admin Office", 888, "Global", "Veg", "Central Office"))

def load_csv_dataset(cursor):
    """Loads patients from patient_data.csv if the file exists."""
    if not os.path.exists(CSV_FILE):
        return

    try:
        df = pd.read_csv(CSV_FILE)
        first_id = int(df.iloc[0]['PatientID'])
        cursor.execute("SELECT count(*) FROM users WHERE id=?", (first_id,))
        if cursor.fetchone()[0] > 0:
            return 
        
        print(f"Loading patients from {CSV_FILE}...")
        
        default_pw = hash_password("1234")
        cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                   ("admin_doc", default_pw, "Doctor", "Dr. CSV Admin", 999, "Global", "Veg", "General Hospital"))
        
        today = str(datetime.date.today())
        
        for index, row in df.iterrows():
            pid = int(row['PatientID'])
            name = row['Name']
            sugar = float(row['Blood_Sugar'])
            chol = float(row['Cholesterol'])
            bp = int(row['BP_Systolic'])
            hb = float(row['Hemoglobin'])
            ht = float(row['Height'])
            wt = float(row['Weight'])
            hosp = row['Hospital']
            meds = row['Medication']
            
            cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (str(pid), default_pw, "Patient", name, pid, "Global", "Non-Veg", hosp))
            
            bmi = 0
            if ht > 0: bmi = round(wt / ((ht/100) ** 2), 2)
            
            cursor.execute("""INSERT INTO reports (patient_id, patient_name, sugar, cholesterol, bp, hemoglobin, height, weight, bmi, doc_id, report_date, medicines, hospital_name) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                           (pid, name, sugar, chol, bp, hb, ht, wt, bmi, 999, today, meds, hosp))
            
        print("CSV Data loaded successfully.")
    except Exception as e:
        print(f"Error loading CSV data: {e}")

def get_doctor_name(doc_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT full_name FROM users WHERE id=?", conn, params=(doc_id,))
        conn.close()
        if not df.empty: return df.iloc[0]['full_name']
        return "Unknown Doctor"
    except: return "Unknown Doctor"

def register_user(username, password, role, name, user_id, region="Global", food_type="Veg", hospital_name=""):
    hashed_pw = hash_password(password)
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                  (username, hashed_pw, role, name, user_id, region, food_type, hospital_name))
        conn.commit()
        conn.close()
        return True, "Success"
    except sqlite3.IntegrityError: return False, "Username exists"

def login_user(username, password):
    hashed_pw = hash_password(password)
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM users WHERE username=? AND password=?", conn, params=(username, hashed_pw))
    conn.close()
    if not df.empty:
        user = df.iloc[0]
        hosp = user['hospital_name'] if 'hospital_name' in user and user['hospital_name'] else "Smart Care Hospital"
        return {
            'Username': user['username'], 'Role': user['role'], 
            'Full_Name': user['full_name'], 
            'Doctor_ID': int(user['id']) if user['role'] == 'Doctor' else None,
            'Patient_ID': int(user['id']) if user['role'] == 'Patient' else None,
            'Region': user['region'], 'Food_Type': user['food_type'],
            'Hospital_Name': hosp
        }
    return None

def calculate_bmi(height_cm, weight_kg):
    if height_cm > 0:
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 2)
    return 0

def save_patient_report(pid, name, s, c, b, h, ht, wt, bmi, doc_id, meds, hospital_name, custom_diet=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = str(datetime.date.today())
    cursor.execute("""INSERT INTO reports (patient_id, patient_name, sugar, cholesterol, bp, hemoglobin, height, weight, bmi, doc_id, report_date, medicines, hospital_name) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                   (pid, name, s, c, b, h, ht, wt, bmi, doc_id, date_str, meds, hospital_name))
    report_id = cursor.lastrowid
    if custom_diet:
        cursor.execute("INSERT INTO prescriptions (report_id, patient_id, diet_plan) VALUES (?, ?, ?)", (report_id, pid, custom_diet))
    conn.commit()
    conn.close()
    return report_id

def delete_patient_report(report_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM reports WHERE report_id=?", (report_id,))
    conn.commit()
    conn.close()
    return True

def fetch_doctor_patients(doc_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM reports WHERE doc_id=?", conn, params=(doc_id,))
    conn.close()
    if not df.empty:
        cols_map = {
            'report_id': 'Report_ID', 'patient_id': 'Patient_ID', 'patient_name': 'Patient_Name',
            'report_date': 'Report_Date', 'sugar': 'Sugar_Fasting', 'cholesterol': 'Cholesterol_Total',
            'bp': 'BP_Systolic', 'hemoglobin': 'Hemoglobin', 'medicines': 'Medicines',
            'height': 'Height', 'weight': 'Weight', 'bmi': 'BMI'
        }
        if 'hospital_name' in df.columns:
            cols_map['hospital_name'] = 'Hospital'
        df = df.rename(columns=cols_map)
    return df

def get_patient_history(pid):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM reports WHERE patient_id=?", conn, params=(pid,))
    presc_df = pd.read_sql_query("SELECT * FROM prescriptions WHERE patient_id=?", conn, params=(pid,))
    conn.close()
    if not df.empty:
        cols_map = {
            'report_id': 'Report_ID', 'report_date': 'Report_Date', 'sugar': 'Sugar_Fasting', 
            'cholesterol': 'Cholesterol_Total', 'bp': 'BP_Systolic', 'hemoglobin': 'Hemoglobin',
            'height': 'Height', 'weight': 'Weight', 'bmi': 'BMI', 'medicines': 'Medicines'
        }
        if 'hospital_name' in df.columns:
            cols_map['hospital_name'] = 'Hospital_Name'
        df = df.rename(columns=cols_map)
        if not presc_df.empty: df['Doctor_Note'] = presc_df.iloc[-1]['diet_plan']
        else: df['Doctor_Note'] = None
    return df

def get_all_patients_summary():
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT patient_id as 'ID', patient_name as 'Name', 
           hospital_name as 'Hospital', report_date as 'Last Report'
    FROM reports
    GROUP BY patient_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def analyze_health(record):
    diagnosis = []
    avoid = []
    boost = []
    
    s = record.get('Sugar_Fasting', record.get('sugar', 0))
    c = record.get('Cholesterol_Total', record.get('cholesterol', 0))
    b = record.get('BP_Systolic', record.get('bp', 0))
    h = record.get('Hemoglobin', record.get('hemoglobin', 0))
    bmi = record.get('BMI', record.get('bmi', 0))

    if s > 126: 
        diagnosis.append("Diabetes (Type 2)")
        avoid.extend(["White Rice", "Potatoes", "White Bread", "Sugary Drinks", "Cakes", "Processed Snacks", "Ice Cream"])
        boost.extend(["Bitter Gourd", "Fenugreek", "Barley", "Jamun", "Spinach", "Whole Grains", "Legumes", "Quinoa"])
    if c > 200: 
        diagnosis.append("High Cholesterol")
        avoid.extend(["Red Meat", "Cheese", "Fried Foods", "Butter", "Palm Oil", "Egg Yolks"])
        boost.extend(["Oats", "Garlic", "Walnuts", "Almonds", "Avocados", "Fatty Fish (Salmon)", "Olive Oil"])
    if b > 140: 
        diagnosis.append("Hypertension")
        avoid.extend(["Pickles", "Papad", "Salted Nuts", "Canned Soups", "Processed Meats", "Excess Salt"])
        boost.extend(["Bananas", "Spinach", "Beetroot", "Watermelon", "Curd", "Coconut Water"])
    if h < 12 and h > 0: 
        diagnosis.append("Anemia")
        avoid.extend(["Tea/Coffee with meals", "Calcium-rich foods with Iron"])
        boost.extend(["Dates", "Pomegranate", "Drumstick Leaves", "Beetroot", "Red Meat", "Jaggery"])
    if bmi > 25:
        diagnosis.append(f"Overweight (BMI {bmi})")
        avoid.extend(["High Calorie Snacks", "Sugary Drinks", "Fast Food", "Ice Cream"])
        boost.extend(["High Fiber Veggies", "Water", "Cucumber", "Melons", "Broccoli"])
    elif bmi < 18.5 and bmi > 0:
        diagnosis.append(f"Underweight (BMI {bmi})")
        boost.extend(["Nuts", "Dairy", "Protein Shakes", "Peanut Butter", "Bananas", "Ghee"])
    
    return {"diagnosis": diagnosis, "avoid": list(set(avoid)), "boost": list(set(boost))}

def get_doc_appointments(doc_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM appointments WHERE doc_id=?", conn, params=(doc_id,))
    conn.close()
    return df

# --- ADMIN / AVAILABILITY FUNCTIONS ---
def get_all_hospitals():
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT DISTINCT hospital_name FROM users WHERE role='Doctor'", conn)
        return df['hospital_name'].tolist()
    except: return []
    finally: conn.close()

def get_doctors_by_hospital(hosp_name):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT id, full_name FROM users WHERE role='Doctor' AND hospital_name=?", conn, params=(hosp_name,))
        return df
    except: return pd.DataFrame()
    finally: conn.close()

def get_all_doctors():
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT id, full_name, hospital_name FROM users WHERE role='Doctor'", conn)
        return df
    finally: conn.close()

def add_availability(doc_id, date_obj):
    """Admin adds availability for a doctor."""
    conn = sqlite3.connect(DB_NAME)
    try:
        date_str = str(date_obj)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM availability WHERE doc_id=? AND available_date=?", (doc_id, date_str))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO availability (doc_id, available_date, is_booked) VALUES (?, ?, 0)", (doc_id, date_str))
            conn.commit()
            return True
        return False
    finally: conn.close()

def get_available_dates(doc_id):
    """Get dates where is_booked=0 for a specific doctor."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT available_date FROM availability WHERE doc_id=? AND is_booked=0 ORDER BY available_date", conn, params=(doc_id,))
        return df['available_date'].tolist()
    finally: conn.close()

# --- APPOINTMENT WORKFLOW UPDATES ---
def request_appointment(pid, name, doc_id, date_str):
    """Patient requests an appointment (Status: Requested). Slot is held."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 1. Insert Appointment
    cursor.execute("INSERT INTO appointments (patient_id, patient_name, doc_id, status, date_requested, admin_message) VALUES (?, ?, ?, ?, ?, ?)", 
                   (pid, name, doc_id, "Requested", date_str, "Waiting for Confirmation"))
    # 2. Update Availability to booked so no one else takes it
    cursor.execute("UPDATE availability SET is_booked=1 WHERE doc_id=? AND available_date=?", (doc_id, date_str))
    conn.commit()
    conn.close()

def get_pending_appointments():
    """For Admin: Get all requests needing confirmation."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM appointments WHERE status='Requested'", conn)
        return df
    finally: conn.close()

def confirm_appointment(appt_id, message):
    """Admin confirms request and adds message."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status='Confirmed', admin_message=? WHERE appt_id=?", (message, appt_id))
    conn.commit()
    conn.close()
    return True

def get_patient_appointments(pid):
    """Get history for patient portal."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM appointments WHERE patient_id=? ORDER BY date_requested DESC", conn, params=(pid,))
        return df
    finally: conn.close()