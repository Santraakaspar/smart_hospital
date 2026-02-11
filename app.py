import streamlit as st
import logic
import chatbot
import pandas as pd
from fpdf import FPDF
import datetime
import os

st.set_page_config(page_title="NutriScript-AI System", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# --- INJECT CUSTOM CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

# --- FORCE DB INITIALIZATION ---
logic.init_db()

# --- CHECK FOR TEXT SHAPER ---
try:
    import uharfbuzz
    HAS_SHAPER = True
except ImportError:
    HAS_SHAPER = False

# --- PDF GENERATOR ---
class PDF(FPDF):
    def header(self):
        pass 
    def footer(self):
        self.set_y(-15) 
        self.set_font('Arial', 'I', 8) 
        self.cell(0, 10, 'Powered by NutriScript-AI', align='C')

def generate_pdf_report(patient_name, doctor_name, hospital_name, vitals, analysis, recipes, language="English", doctor_note=None, medicines=None):
    pdf = None
    if HAS_SHAPER:
        try: pdf = PDF(text_shaping=True)
        except TypeError: pdf = PDF()
    else: pdf = PDF()
        
    pdf.add_page()
    
    font_path = None
    if os.path.exists("Nirmala.ttf"): font_path = "Nirmala.ttf"
    elif os.path.exists("Nirmala.ttc"): font_path = "Nirmala.ttc"
        
    has_font = False
    if font_path:
        try:
            pdf.add_font("Nirmala", style="", fname=font_path)
            pdf.add_font("Nirmala", style="B", fname=font_path) 
            has_font = True
        except:
            try: pdf.add_font("Nirmala", fname=font_path); has_font = True
            except: has_font = False
    
    effective_lang = language if has_font else "English"

    def set_native_font(style='', size=12):
        if has_font: pdf.set_font("Nirmala", style=style, size=size)
        else: pdf.set_font("Arial", style=style, size=size)

    t = lambda k: logic.get_trans(effective_lang, k, 'ui')
    
    set_native_font('B', 18)
    pdf.cell(0, 10, txt=hospital_name, ln=1, align='C')
    set_native_font('', 12)
    pdf.cell(0, 10, txt=t("Header"), ln=1, align='C')
    pdf.ln(10)
    
    set_native_font('B', 12)
    pdf.cell(100, 10, txt=f"{t('Patient')}: {patient_name}", ln=0)
    pdf.cell(0, 10, txt=f"{t('Date')}: {datetime.date.today()}", ln=1)
    pdf.cell(0, 10, txt=f"{t('Doctor')}: Dr. {doctor_name}", ln=1)
    pdf.ln(5); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)

    set_native_font('B', 12); pdf.cell(0, 10, txt=t("Vitals_Title"), ln=1); set_native_font('', 12)
    pdf.cell(100, 10, txt=f"   - {t('Sugar')}: {vitals.get('Sugar_Fasting', 'N/A')} mg/dL", ln=0)
    pdf.cell(0, 10, txt=f"   - {t('BP')}: {vitals.get('BP_Systolic', 'N/A')} mmHg", ln=1)
    pdf.cell(100, 10, txt=f"   - {t('BMI')}: {vitals.get('BMI', 'N/A')}", ln=0)
    pdf.cell(0, 10, txt=f"   - {t('Weight')}: {vitals.get('Weight', 'N/A')} kg", ln=1)
    pdf.cell(100, 10, txt=f"   - Cholesterol: {vitals.get('Cholesterol_Total', 'N/A')} mg/dL", ln=0)
    pdf.cell(0, 10, txt=f"   - Hemoglobin: {vitals.get('Hemoglobin', 'N/A')} g/dL", ln=1)
    pdf.ln(5)

    if medicines:
        set_native_font('B', 12); pdf.cell(0, 10, txt=t("Medicines_Title") + ":", ln=1); set_native_font('', 12)
        pdf.multi_cell(0, 10, txt=medicines); pdf.ln(5)
    
    set_native_font('B', 12); pdf.cell(0, 10, txt=t("Diagnosis_Title") + ":", ln=1); set_native_font('', 12)
    for d in analysis['diagnosis']: pdf.cell(0, 10, txt=f"   - {d}", ln=1)
    pdf.ln(5)
    
    set_native_font('B', 12); pdf.cell(0, 10, txt=t("Diet_Title") + ":", ln=1); set_native_font('', 12)
    if doctor_note:
        pdf.multi_cell(0, 10, txt=doctor_note)
    else:
        avoid_items = [logic.get_ingredient_name(x, effective_lang) for x in analysis['avoid']]
        eat_items = [logic.get_ingredient_name(x, effective_lang) for x in analysis['boost']]
        
        avoid_str = ", ".join(avoid_items)
        eat_str = ", ".join(eat_items)
        pdf.multi_cell(0, 10, txt=f"[{t('Avoid')}]: {avoid_str}")
        pdf.ln(2)
        pdf.multi_cell(0, 10, txt=f"[{t('Eat')}]: {eat_str}")
        
    res = pdf.output()
    if isinstance(res, str): return res.encode('latin-1', 'replace')
    return bytes(res)

st.markdown("""<style>.stButton>button { background: linear-gradient(135deg, #00b09b, #96c93d); color: white; border-radius: 20px; }</style>""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.update({'logged_in': False, 'role': None, 'username': None, 'fetched_data': None})

# Form Data Keys
if 'form_name' not in st.session_state: st.session_state.form_name = ""
if 'form_height' not in st.session_state: st.session_state.form_height = 160.0
if 'form_weight' not in st.session_state: st.session_state.form_weight = 60.0
if 'form_bp' not in st.session_state: st.session_state.form_bp = 120
if 'form_sugar' not in st.session_state: st.session_state.form_sugar = 90.0
if 'form_chol' not in st.session_state: st.session_state.form_chol = 150.0
if 'form_hemo' not in st.session_state: st.session_state.form_hemo = 13.0
if 'form_meds' not in st.session_state: st.session_state.form_meds = "Metformin 500mg - Once daily"
if 'diet_avoid' not in st.session_state: st.session_state['diet_avoid'] = ""
if 'diet_boost' not in st.session_state: st.session_state['diet_boost'] = ""


if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; color: var(--primary); font-size: 3rem;'>🏥 NutriScript-AI System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: var(--text-secondary); margin-bottom: 2rem;'>Advanced Patient Management & Nutrition System</p>", unsafe_allow_html=True)

    
    t1, t2, t3 = st.tabs(["Patient/Doctor Login", "Admin Office Login", "Register New User"])
    
    with t1:
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Login", key="main_login"):
            user = logic.login_user(u, p)
            if user: st.session_state.update({'logged_in': True, **user, 'doc_id': user['Doctor_ID'], 'patient_id': user['Patient_ID'], 'hospital_name': user.get('Hospital_Name', '')}); st.rerun()
            else: st.error("Invalid Credentials")
            
    with t2:
        st.info("⚠️ Restricted Area for Admin Office Only")
        au, ap = st.text_input("Admin Username"), st.text_input("Admin Password", type="password")
        if st.button("Admin Login"):
            user = logic.login_user(au, ap)
            if user and user['Role'] == 'Admin':
                st.session_state.update({'logged_in': True, **user}); st.rerun()
            else:
                st.error("Invalid Admin Credentials")

    with t3:
        role = st.selectbox("I am a...", ["Doctor", "Patient"])
        n, u_reg, p_reg, uid = st.text_input("Full Name"), st.text_input("New Username"), st.text_input("New Password", type="password"), st.number_input("Medical License ID / Patient ID", min_value=1)
        h_name = ""
        if role == "Doctor": h_name = st.text_input("Hospital Name", placeholder="e.g. Apollo Hospital")
        if st.button("Register"):
            if role == "Doctor" and not h_name: st.error("Please enter Hospital Name.")
            elif logic.register_user(u_reg, p_reg, role, n, uid, hospital_name=h_name): st.success("Registered! Please Login.")
            else: st.error("Username taken.")

elif st.session_state['Role'] == 'Admin':
    with st.sidebar:
        st.title("🏢 Admin Office"); st.write(f"Logged in as: Admin"); 
        if st.button("Logout"): st.session_state.clear(); st.rerun()
    
    st.title("Admin Dashboard")
    
    at1, at2, at3 = st.tabs(["🗓️ Add Availability", "📩 Pending Requests", "📋 Doctor Schedules"])
    
    # 1. ADD AVAILABILITY
    with at1:
        st.subheader("Add Doctor Availability")
        docs_df = logic.get_all_doctors()
        if not docs_df.empty:
            doc_map = {f"{row['full_name']} ({row['hospital_name']})": row['id'] for index, row in docs_df.iterrows()}
            c1, c2 = st.columns(2)
            with c1:
                sel_doc = st.selectbox("Select Doctor", list(doc_map.keys()))
                doc_id = doc_map[sel_doc]
            with c2:
                sel_date = st.date_input("Select Date to Mark Available", min_value=datetime.date.today())
            
            if st.button("✅ Add Available Date"):
                if logic.add_availability(doc_id, sel_date):
                    st.success(f"Added availability for {sel_doc} on {sel_date}")
                else:
                    st.warning("This date is already marked available.")
        else:
            st.warning("No Doctors Registered.")

    # 2. PENDING REQUESTS (Dropdown Menu for Admin)
    with at2:
        st.subheader("Manage Appointment Requests")
        pending = logic.get_pending_appointments()
        if not pending.empty:
            # Create readable list for dropdown
            req_list = [f"#{row['appt_id']} - {row['patient_name']} -> Doc ID {row['doc_id']} ({row['date_requested']})" for index, row in pending.iterrows()]
            
            sel_req_str = st.selectbox("Select Pending Request", req_list)
            
            # Extract Appt ID
            sel_appt_id = int(sel_req_str.split(" - ")[0].replace("#", ""))
            
            st.write("---")
            admin_msg = st.text_input("Message to Patient (e.g. 'Bring ID proof', 'Come at 10 AM')", value="Confirmed. Please arrive on time.")
            
            if st.button("✅ Confirm & Notify Patient"):
                logic.confirm_appointment(sel_appt_id, admin_msg)
                st.success("Appointment Confirmed! Notification sent to Patient.")
                st.rerun()
        else:
            st.info("No pending requests.")

    # 3. VIEW SCHEDULES
    with at3:
        st.subheader("View Doctor Schedules")
        docs_df = logic.get_all_doctors()
        if not docs_df.empty:
            doc_map_view = {f"{row['full_name']} ({row['hospital_name']})": row['id'] for index, row in docs_df.iterrows()}
            view_doc = st.selectbox("Select Doctor to View", list(doc_map_view.keys()), key="view_sched")
            view_id = doc_map_view[view_doc]
            
            dates = logic.get_available_dates(view_id)
            if dates:
                st.write(f"**Available Dates for {view_doc}:**")
                for d in dates:
                    st.markdown(f"- 🗓️ {d}")
            else:
                st.info("No future availability added.")

elif st.session_state['Role'] == 'Doctor':
    with st.sidebar:
        st.title("👨‍⚕️ Doctor Dashboard"); st.write(f"Dr. {st.session_state['Full_Name']}"); st.caption(f"🏥 {st.session_state.get('hospital_name', 'Unknown Hospital')}")
        if st.button("Logout"): st.session_state.clear(); st.rerun()

    tab1, tab2, tab3 = st.tabs(["🩺 New Entry", "📂 Records", "📅 My Schedule"])
    
    with tab1:
        # --- INIT SESSION KEYS ---
        if 'form_name' not in st.session_state: st.session_state.form_name = ""
        if 'form_height' not in st.session_state: st.session_state.form_height = 160.0
        if 'form_weight' not in st.session_state: st.session_state.form_weight = 60.0
        if 'form_bp' not in st.session_state: st.session_state.form_bp = 120
        if 'form_sugar' not in st.session_state: st.session_state.form_sugar = 90.0
        if 'form_chol' not in st.session_state: st.session_state.form_chol = 150.0
        if 'form_hemo' not in st.session_state: st.session_state.form_hemo = 13.0
        if 'form_meds' not in st.session_state: st.session_state.form_meds = "Metformin 500mg - Once daily"

        with st.expander("🔍 Search Patient Database (Lab Results)", expanded=True):
            search_query = st.text_input("Search by Name or ID")
            df_all = logic.get_all_patients_summary()
            if not df_all.empty:
                if search_query:
                    df_all = df_all[df_all['Name'].astype(str).str.contains(search_query, case=False) | df_all['ID'].astype(str).str.contains(search_query)]
                st.dataframe(df_all, use_container_width=True, hide_index=True)
                st.caption("👆 Use the ID from the table above to fetch patient details.")
            else: st.info("No records found in the lab database.")

        st.divider(); st.subheader("Fetch & Update Patient")
        c1, c2 = st.columns([3,1])
        pid = c1.number_input("Enter Patient ID to Fetch", min_value=1, value=1001)
        if c2.button("Fetch Data"):
            hist = logic.get_patient_history(pid)
            if not hist.empty: 
                record = hist.iloc[-1].to_dict()
                st.session_state.fetched_data = record
                
                # --- AUTO-FILL LOGIC ---
                st.session_state.form_name = record.get('Patient_Name', '')
                st.session_state.form_height = float(record.get('Height', 160))
                st.session_state.form_weight = float(record.get('Weight', 60))
                st.session_state.form_bp = int(record.get('BP_Systolic', 120))
                st.session_state.form_sugar = float(record.get('Sugar_Fasting', 90))
                st.session_state.form_chol = float(record.get('Cholesterol_Total', 150))
                st.session_state.form_hemo = float(record.get('Hemoglobin', 13))
                
                if record.get('Medicines'):
                    st.session_state.form_meds = record.get('Medicines')
                
                analysis = logic.analyze_health(record)
                st.session_state['diet_avoid'] = ", ".join(analysis['avoid'])
                st.session_state['diet_boost'] = ", ".join(analysis['boost'])
                
                if not st.session_state['diet_avoid']: st.session_state['diet_avoid'] = "No specific restrictions detected."
                if not st.session_state['diet_boost']: st.session_state['diet_boost'] = "Balanced diet recommended."

                st.success(f"Loaded: {st.session_state.form_name}")
                st.rerun() 
            else: 
                st.session_state.fetched_data = {}
                st.session_state['diet_avoid'] = ""
                st.session_state['diet_boost'] = ""
                st.warning("ID not found.")

        # --- FORM INPUTS ---
        st.subheader("1. Vitals & Biometrics")
        col1, col2, col3, col4 = st.columns(4)
        name = col1.text_input("Name", key="form_name")
        h = col2.number_input("Height (cm)", key="form_height")
        w = col3.number_input("Weight (kg)", key="form_weight")
        bp = col4.number_input("BP (mmHg)", key="form_bp")
        
        col5, col6, col7 = st.columns(3)
        sugar = col5.number_input("Sugar (mg/dL)", key="form_sugar")
        chol = col6.number_input("Cholesterol", key="form_chol")
        hemo = col7.number_input("Hemoglobin", key="form_hemo")
        
        bmi = logic.calculate_bmi(h, w)
        analysis_rt = logic.analyze_health({'sugar': sugar, 'bp': bp, 'chol': chol, 'hemoglobin': hemo, 'bmi': bmi})
        st.info(f"**Calculated BMI:** {bmi} | **Auto-Diagnosis:** {', '.join(analysis_rt['diagnosis'])}")
        
        st.subheader("2. Medication & Diet Plan")
        meds = st.text_area("Prescribe Medicines (One per line)", key="form_meds")
        
        st.markdown("#### **AI-Suggested Diet Plan (Editable)**")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            avoid_input = st.text_area("🚫 Foods to Avoid", key="diet_avoid", height=120)
        with col_d2:
            eat_input = st.text_area("✅ Recommended Foods", key="diet_boost", height=120)
            
        final_diet_note = f"**AVOID:** {avoid_input}\n\n**RECOMMENDED:** {eat_input}"
        
        if st.button("💾 Save Record & Prescription"):
            hosp = st.session_state.get('hospital_name', 'General')
            rid = logic.save_patient_report(pid, name, sugar, chol, bp, hemo, h, w, bmi, st.session_state['doc_id'], meds, hosp, final_diet_note)
            st.success(f"Saved Record #{rid} for {hosp}")
            
    with tab2:
        df = logic.fetch_doctor_patients(st.session_state['doc_id'])
        if not df.empty: st.dataframe(df)
        else: st.info("No records.")
    with tab3:
        st.subheader("📅 Confirmed Appointments")
        apps = logic.get_doc_appointments(st.session_state['doc_id'])
        if not apps.empty: 
            st.table(apps[['patient_name', 'date_requested', 'status', 'admin_message']])
        else: st.info("No appointments scheduled.")

elif st.session_state['Role'] == 'Patient':
    # Initialize language in session state
    if 'patient_lang' not in st.session_state:
        st.session_state.patient_lang = 'English'
    
    with st.sidebar:
        st.title("👤 Patient Portal")
        lang = st.selectbox("🌐 Select Language", list(logic.UI_TRANSLATIONS.keys()), index=list(logic.UI_TRANSLATIONS.keys()).index(st.session_state.patient_lang))
        if lang != st.session_state.patient_lang:
            st.session_state.patient_lang = lang
            st.rerun()
        t = lambda k: logic.get_trans(st.session_state.patient_lang, k, 'ui')
        if st.button("Logout"): st.session_state.clear(); st.rerun()

    if not HAS_SHAPER: st.error("⚠️ **Text Shaping Library Missing:** Install `uharfbuzz` for correct Tamil/Hindi letters.")
    if not (os.path.exists("Nirmala.ttf") or os.path.exists("Nirmala.ttc")): st.warning("⚠️ **Font Missing:** Copy `Nirmala.ttf` to this folder.")

    pid = st.session_state['patient_id']
    history = logic.get_patient_history(pid)
    if not history.empty:
        latest = history.iloc[-1]
        analysis = logic.analyze_health(latest)
        doc_name = logic.get_doctor_name(latest['doc_id'])
        hosp_name = latest.get('Hospital_Name', 'Smart Hospital')

        st.title(f"{t('Header')} - {st.session_state['Full_Name']}")
        
        # --- VITALS ---
        st.subheader("📊 Your Vitals")
        
        # Custom CSS Card for Vitals
        def card(label, value, delta=None, color="primary"):
            delta_html = f"<div style='color: var(--{color}); font-size: 0.9rem; margin-top: 5px;'>{delta}</div>" if delta else ""
            return f"""
            <div class="custom-card">
                <div class="card-header">{label}</div>
                <div class="card-value">{value}</div>
                {delta_html}
            </div>
            """

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.markdown(card("BMI", latest.get('BMI', 'N/A'), f"{latest.get('Weight', 'N/A')} kg", "secondary"), unsafe_allow_html=True)
        with c2: st.markdown(card(t("Sugar"), f"{latest.get('Sugar_Fasting', 'N/A')} mg/dL"), unsafe_allow_html=True)
        with c3: st.markdown(card(t("BP"), f"{latest.get('BP_Systolic', 'N/A')} mmHg"), unsafe_allow_html=True)
        with c4: st.markdown(card("Cholesterol", f"{latest.get('Cholesterol_Total', 'N/A')} mg/dL"), unsafe_allow_html=True)
        with c5: st.markdown(card("Hemoglobin", f"{latest.get('Hemoglobin', 'N/A')} g/dL"), unsafe_allow_html=True)

        st.subheader("⚠️ Health Alerts")
        alerts_found = False
        try:
            if float(latest.get('Sugar_Fasting', 0)) > 140: st.error("⚠️ **High Blood Sugar Detected**"); alerts_found = True
        except: pass
        try:
            if float(latest.get('BP_Systolic', 0)) > 130: st.error("⚠️ **High Blood Pressure**"); alerts_found = True
        except: pass
        try:
            if float(latest.get('Cholesterol_Total', 0)) > 200: st.error("⚠️ **High Cholesterol**"); alerts_found = True
        except: pass
        try:
            hb = float(latest.get('Hemoglobin', 0))
            if hb > 0 and hb < 12: st.warning("⚠️ **Low Hemoglobin (Anemia)**"); alerts_found = True
        except: pass
        if not alerts_found: st.success("✅ All vitals look good within normal range!")

        # --- VITALS PROGRESS SECTION ---
        st.divider()
        st.subheader("📈 Vitals Progress")
        
        # Time period filter
        time_periods = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
        col_time = st.columns(len(time_periods))
        selected_period = "1M"
        for idx, (label, days) in enumerate(time_periods.items()):
            if col_time[idx].button(label, use_container_width=True):
                st.session_state.vitals_period = label
        
        selected_period = st.session_state.get('vitals_period', '1M')
        days_back = time_periods[selected_period]
        
        # Filter history by date
        history['Report_Date'] = pd.to_datetime(history['Report_Date'])
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        filtered_history = history[history['Report_Date'] >= cutoff_date].sort_values('Report_Date')
        
        if not filtered_history.empty:
            # Metric selector
            metric = st.selectbox("Select Metric to Track", 
                                 ["Blood Sugar (mg/dL)", "Blood Pressure (mmHg)", "Cholesterol (mg/dL)", "Hemoglobin (g/dL)", "BMI", "Weight (kg)"],
                                 key="vital_metric")
            
            # Prepare data for chart
            chart_data = filtered_history[['Report_Date']].copy()
            
            if metric == "Blood Sugar (mg/dL)":
                chart_data['Value'] = filtered_history['Sugar_Fasting'].astype(float)
                chart_data['Metric'] = 'Blood Sugar'
                normal_range = (70, 100)
            elif metric == "Blood Pressure (mmHg)":
                chart_data['Value'] = filtered_history['BP_Systolic'].astype(float)
                chart_data['Metric'] = 'Blood Pressure'
                normal_range = (90, 120)
            elif metric == "Cholesterol (mg/dL)":
                chart_data['Value'] = filtered_history['Cholesterol_Total'].astype(float)
                chart_data['Metric'] = 'Cholesterol'
                normal_range = (0, 200)
            elif metric == "Hemoglobin (g/dL)":
                chart_data['Value'] = filtered_history['Hemoglobin'].astype(float)
                chart_data['Metric'] = 'Hemoglobin'
                normal_range = (12, 17)
            elif metric == "BMI":
                chart_data['Value'] = filtered_history['BMI'].astype(float)
                chart_data['Metric'] = 'BMI'
                normal_range = (18.5, 24.9)
            else:  # Weight
                chart_data['Value'] = filtered_history['Weight'].astype(float)
                chart_data['Metric'] = 'Weight'
                normal_range = None
            
            # Display chart
            st.line_chart(
                data=chart_data.set_index('Report_Date')['Value'],
                use_container_width=True,
                height=400
            )
            
            # Statistics
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            avg_value = chart_data['Value'].mean()
            latest_value = chart_data['Value'].iloc[-1]
            max_value = chart_data['Value'].max()
            min_value = chart_data['Value'].min()
            
            trend = "📈 Increasing" if len(chart_data) > 1 and chart_data['Value'].iloc[-1] > chart_data['Value'].iloc[0] else "📉 Decreasing" if len(chart_data) > 1 else "➡️ Stable"
            trend_pct = abs((latest_value - chart_data['Value'].iloc[0]) / chart_data['Value'].iloc[0] * 100) if len(chart_data) > 1 and chart_data['Value'].iloc[0] != 0 else 0
            
            with col_stats1:
                st.metric("Average", f"{avg_value:.1f}", delta=None)
            with col_stats2:
                st.metric("Latest", f"{latest_value:.1f}", delta=f"{trend_pct:.1f}%" if len(chart_data) > 1 else None)
            with col_stats3:
                st.metric("Highest", f"{max_value:.1f}")
            with col_stats4:
                st.metric("Lowest", f"{min_value:.1f}")
            
            st.caption(f"📊 {trend}")
            
            # Recent readings
            st.subheader("📋 Recent Readings")
            recent_display = filtered_history[['Report_Date', 'Sugar_Fasting', 'BP_Systolic', 'Cholesterol_Total', 'Hemoglobin', 'BMI']].tail(5).copy()
            recent_display.columns = ['Date', 'Sugar (mg/dL)', 'BP (mmHg)', 'Cholesterol', 'Hemoglobin', 'BMI']
            recent_display['Date'] = pd.to_datetime(recent_display['Date']).dt.strftime('%Y-%m-%d')
            st.dataframe(recent_display, use_container_width=True, hide_index=True)
        else:
            st.info("📅 No records found for the selected time period. Check back after your next visit!")

        with st.container(border=True):
            st.subheader(f"💊 {t('Medicines_Title')}"); st.text(latest['Medicines'] if latest['Medicines'] else "No medicines prescribed.")

        st.subheader("🥗 Personalized Diet Plan")
        c_av, c_ea = st.columns(2)
        with c_av:
            st.error(f"**{t('Avoid')}:**")
            if analysis['avoid']:
                for item in analysis['avoid']: st.markdown(f"❌ {logic.get_ingredient_name(item, st.session_state.patient_lang)}")
            else: st.write("None")
        with c_ea:
            st.success(f"**{t('Eat')}:**")
            if analysis['boost']:
                for item in analysis['boost']: st.markdown(f"✅ {logic.get_ingredient_name(item, st.session_state.patient_lang)}")
            else: st.write("Balanced Diet Recommended")

        st.divider()
        c_app, c_pdf = st.columns(2)
        
        # --- APPOINTMENT REQUEST & STATUS ---
        with c_app:
            st.subheader(f"🏥 Appointments")
            
            # View History First
            appt_hist = logic.get_patient_appointments(pid)
            if not appt_hist.empty:
                st.caption("Recent Requests:")
                for i, r in appt_hist.iterrows():
                    status_icon = "⏳" if r['status'] == 'Requested' else "✅"
                    msg_display = f"- **Admin Msg:** {r['admin_message']}" if r['admin_message'] else ""
                    st.write(f"{status_icon} **{r['date_requested']}**: {r['status']} {msg_display}")

            st.write("---")
            st.info("Request New Appointment")
            hospitals = logic.get_all_hospitals()
            
            if not hospitals:
                st.warning("No Registered Hospitals found.")
            else:
                sel_hosp = st.selectbox("Select Hospital", hospitals)
                if sel_hosp:
                    docs_df = logic.get_doctors_by_hospital(sel_hosp)
                    if not docs_df.empty:
                        doc_map = {row['full_name']: row['id'] for index, row in docs_df.iterrows()}
                        sel_doc_name = st.selectbox("Select Doctor", list(doc_map.keys()))
                        target_doc_id = doc_map[sel_doc_name]
                        
                        avail_dates = logic.get_available_dates(target_doc_id)
                        
                        if avail_dates:
                            sel_avail_date = st.selectbox("Select Available Date", avail_dates)
                            if st.button("Request Appointment"):
                                logic.request_appointment(pid, st.session_state['Full_Name'], target_doc_id, sel_avail_date)
                                st.success(f"⏳ Request sent to Admin for Dr. {sel_doc_name} on {sel_avail_date}. Please wait for confirmation.")
                                st.rerun()
                        else:
                            st.warning("No available dates. Please contact Admin Office.")
                    else:
                        st.warning("No doctors registered at this hospital.")
            
        with c_pdf:
            st.subheader("📄 Report")
            pdf_data = generate_pdf_report(patient_name=st.session_state['Full_Name'], doctor_name=doc_name, hospital_name=hosp_name, vitals=latest, analysis=analysis, recipes=[], language=st.session_state.patient_lang, doctor_note=latest['Doctor_Note'], medicines=latest['Medicines'])
            st.download_button(f"Download Report ({st.session_state.patient_lang})", data=pdf_data, file_name=f"Report_{st.session_state.patient_lang}.pdf", mime="application/pdf")
        
        st.divider()
        st.subheader("💬 AI Nutrition Assistant")
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        for role, text in st.session_state.chat_history:
            with st.chat_message(role): st.markdown(text)
        
        if user_query := st.chat_input("Ask about recipes (e.g., 'Breakfast ideas', 'Dinner options')..."):
            st.session_state.chat_history.append(("user", user_query))
            with st.chat_message("user"): st.markdown(user_query)
            bot_reply = chatbot.get_response(user_query, analysis['diagnosis'], st.session_state.patient_lang)
            st.session_state.chat_history.append(("assistant", bot_reply))
            with st.chat_message("assistant"): st.markdown(bot_reply)
    else:
        st.warning("No records found. Please visit a doctor.")