import flet as ft
import logic
import chatbot
import datetime

# --- UTILS ---
def get_greeting():
    h = datetime.datetime.now().hour
    if h < 12: return "Good Morning"
    elif h < 18: return "Good Afternoon"
    return "Good Evening"

def main(page: ft.Page):
    # --- PAGE CONFIG ---
    page.title = "NutriScript-AI System"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#111418"
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    
    # Init DB
    logic.init_db()

    # --- STATE ---
    user_state = {
        "logged_in": False,
        "user_info": None
    }

    # --- ASSETS / STYLES ---
    primary_color = "#00897B"
    secondary_color = "#E0F2F1"
    error_color = "#F44336"
    
    # --- VIEWS ---

    def login_view():
        # --- DEFINITIONS ---
        
        # 1. Patient/Doctor
        u1 = ft.TextField(label="Username", width=300, border_radius=10)
        p1 = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True, border_radius=10)
        e1 = ft.Text(color="red", size=12)

        def login_click_main(e):
            if not u1.value or not p1.value:
                e1.value = "Please enter credentials."
                page.update()
                return
            user = logic.login_user(u1.value, p1.value)
            print(f"DEBUG: Login Result: {user}")
            if user:
                user_state["logged_in"] = True
                user_state["user_info"] = user
                show_dashboard()
            else:
                e1.value = "Invalid Credentials."
                page.update()

        # 2. Admin
        u2 = ft.TextField(label="Admin Username", width=300, border_radius=10)
        p2 = ft.TextField(label="Admin Password", width=300, password=True, can_reveal_password=True, border_radius=10)
        e2 = ft.Text(color="red", size=12)

        def login_click_admin(e):
            if not u2.value or not p2.value:
                e2.value = "Please enter admin credentials."
                page.update()
                return
            user = logic.login_user(u2.value, p2.value)
            if user and user.get('Role') == 'Admin':
                user_state["logged_in"] = True
                user_state["user_info"] = user
                show_dashboard()
            else:
                e2.value = "Invalid Admin Credentials."
                page.update()

        # 3. Register
        r_role = ft.Dropdown(label="I am a...", options=[ft.dropdown.Option("Doctor"), ft.dropdown.Option("Patient")], width=300)
        r_name = ft.TextField(label="Full Name", width=300)
        r_user = ft.TextField(label="New Username", width=300)
        r_pass = ft.TextField(label="New Password", width=300, password=True, can_reveal_password=True)
        r_uid = ft.TextField(label="Medical ID / Patient ID", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        r_hosp = ft.TextField(label="Hospital Name (Doctors)", width=300)
        r_msg = ft.Text(size=12)

        def register_click(e):
            if not (r_role.value and r_name.value and r_user.value and r_pass.value and r_uid.value):
                r_msg.value = "Please fill all fields."
                r_msg.color = "red"
                page.update()
                return
            
            h_val = r_hosp.value if r_role.value == "Doctor" else ""
            if r_role.value == "Doctor" and not h_val:
                r_msg.value = "Doctor must enter Hospital Name."
                r_msg.color = "red"
                page.update()
                return

            try:
                uid_int = int(r_uid.value)
                if logic.register_user(r_user.value, r_pass.value, r_role.value, r_name.value, uid_int, hospital_name=h_val):
                    r_msg.value = "Registration Successful! Please Login."
                    r_msg.color = "green"
                    
                    # Clear fields
                    r_name.value = ""
                    r_user.value = ""
                    r_pass.value = ""
                    r_uid.value = ""
                    r_hosp.value = ""
                else:
                    r_msg.value = "Username already taken."
                    r_msg.color = "red"
            except ValueError:
                r_msg.value = "ID must be a number."
                r_msg.color = "red"
            page.update()

        # Pre-fill Demo
        u1.value = "1001"
        p1.value = "1234"

        # --- LAYOUT CONSTRUCTION ---
        tab1_content = ft.Container(
            content=ft.Column([
                ft.Text("Patient/Doctor Login", size=20, weight=ft.FontWeight.BOLD),
                u1, p1, e1,
                ft.ElevatedButton("Login", on_click=login_click_main, width=300, bgcolor=primary_color, color="white")
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            visible=True
        )

        tab2_content = ft.Container(
            content=ft.Column([
                ft.Text("Admin Office Login", size=20, weight=ft.FontWeight.BOLD, color="orange"),
                u2, p2, e2,
                ft.ElevatedButton("Admin Login", on_click=login_click_admin, width=300, bgcolor="orange", color="white")
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            visible=False
        )

        tab3_content = ft.Container(
            content=ft.Column([
                ft.Text("Create New Account", size=20, weight=ft.FontWeight.BOLD),
                r_role, r_name, r_user, r_pass, r_uid, r_hosp, r_msg,
                ft.ElevatedButton("Register", on_click=register_click, width=300, bgcolor="blue", color="white")
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            padding=20,
            visible=False
        )

        main_content_area = ft.Column([tab1_content, tab2_content, tab3_content])

        # --- CUSTOM TABS LOGIC ---
        def show_tab(idx):
            tab1_content.visible = (idx == 0)
            tab2_content.visible = (idx == 1)
            tab3_content.visible = (idx == 2)
            
            # Update button styles to show active state
            btn1.style = ft.ButtonStyle(bgcolor=primary_color if idx==0 else "#E0E0E0", color="white" if idx==0 else "black")
            btn2.style = ft.ButtonStyle(bgcolor=primary_color if idx==1 else "#E0E0E0", color="white" if idx==1 else "black")
            btn3.style = ft.ButtonStyle(bgcolor=primary_color if idx==2 else "#E0E0E0", color="white" if idx==2 else "black")
            page.update()

        btn1 = ft.ElevatedButton("Login", on_click=lambda e: show_tab(0), style=ft.ButtonStyle(bgcolor=primary_color, color="white"))
        btn2 = ft.ElevatedButton("Admin", on_click=lambda e: show_tab(1), style=ft.ButtonStyle(bgcolor="#E0E0E0", color="black"))
        btn3 = ft.ElevatedButton("Register", on_click=lambda e: show_tab(2), style=ft.ButtonStyle(bgcolor="#E0E0E0", color="black"))

        return ft.Container(
            content=ft.Column([
                ft.Text("NutriScript-AI System", size=30, weight=ft.FontWeight.BOLD, color=primary_color),
                ft.Text("Smart Hospital Management", size=16, color="#757575"),
                ft.Divider(height=20),
                
                # Tab Handlers
                ft.Row([btn1, btn2, btn3], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                
                ft.Container(content=main_content_area, height=500, width=500, border=ft.border.all(1, "#EEEEEE"), border_radius=10)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor="#FAFAFA"
        )

    def dashboard_view():
        user = user_state["user_info"]
        role = user.get("Role", "User")
        name = user.get("Full_Name", "User")
        pid = user.get("Patient_ID")
        print(f"DEBUG: Dashboard View Loaded. Role: {role}, PID: {pid}")
        
        content_area = ft.Container(expand=True, padding=20)
        
        # --- UI COMPONENTS ---
        def vital_card(title, value, unit, icon, color):
            return ft.Container(
                content=ft.Column([
                    ft.Text(title, size=14, color="#909090", weight=ft.FontWeight.W_500),
                    ft.Row([
                        ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ], spacing=5),
                    ft.Text(unit, size=14, color=color, weight=ft.FontWeight.BOLD)
                ], spacing=5),
                padding=20,
                bgcolor="#1E2329", # Dark card bg
                border_radius=12,
                width=180,
                # border=ft.border.all(1, "#30363D")
            )

        def build_patient_dashboard():
            try:
                print("DEBUG: Building Patient Dashboard")
                if not pid:
                    return ft.Text("Patient ID not found.", color="red")
                    
                history = logic.get_patient_history(pid)
                if history.empty:
                    return ft.Text("No medical records found.", size=20)
                
                latest = history.iloc[-1]
                analysis = logic.analyze_health(latest)
                
                # 1. VITALS SECTION
                vitals_row = ft.Row(
                    controls=[
                        vital_card("BMI", latest.get("BMI", "N/A"), f"{latest.get('Weight','')} kg", "monitor_weight", "#66BB6A"),
                        vital_card("Sugar", latest.get("Sugar_Fasting", "N/A"), "mg/dL", "water_drop", "#42A5F5"),
                        vital_card("Blood Pressure", latest.get("BP_Systolic", "N/A"), "mmHg", "favorite", "#EF5350"),
                        vital_card("Cholesterol", latest.get("Cholesterol_Total", "N/A"), "mg/dL", "fastfood", "#FFA726"),
                        vital_card("Hemoglobin", latest.get("Hemoglobin", "N/A"), "g/dL", "opacity", "#AB47BC"),
                    ],
                    scroll=ft.ScrollMode.ALWAYS
                )
                vitals_container = ft.Container(content=vitals_row, height=180)
                
                # 2. HEALTH ALERTS SECTION (Red Banners)
                alerts_col = ft.Column(spacing=10)
                for d in analysis['diagnosis']:
                    alert_text = d
                    if "Diabetes" in d: alert_text = "High Blood Sugar Detected"
                    elif "Hypertension" in d: alert_text = "High Blood Pressure"
                    elif "Cholesterol" in d: alert_text = "High Cholesterol"
                    
                    alerts_col.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon("warning", color="#FF8A80"),
                                ft.Text(alert_text, color="#FFCCBC", weight=ft.FontWeight.BOLD, size=16)
                            ]),
                            bgcolor="#3E2723", # Dark Red bg
                            border=ft.Border(left=ft.BorderSide(5, "#FF5252")),
                            padding=15,
                            border_radius=5,
                            width=None,
                            expand=True
                        )
                    )
                
                if not analysis['diagnosis']:
                    alerts_col.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon("check_circle", color="#66BB6A"),
                                ft.Text("No Health Alerts - Keep it up!", color="#A5D6A7", weight=ft.FontWeight.BOLD)
                            ]),
                            bgcolor="#1B5E20", # Dark Green bg
                            border=ft.Border(left=ft.BorderSide(5, "#4CAF50")),
                            padding=15,
                            border_radius=5,
                            expand=True
                        )
                    )

                # 3. DIET/RECIPES HINT
                diet_hint = ft.Container(
                    content=ft.Row([
                        ft.Text("Ask about recipes (e.g., 'Breakfast ideas', 'Dinner options')...", color="#909090", italic=True),
                        ft.Icon("send", color="#909090", size=16)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="#202124", 
                    padding=15,
                    border_radius=30,
                    border=ft.Border.all(1, "#30363D"),
                    margin=ft.Margin.only(top=10)
                )

                return ft.Column([
                    ft.Text(f"Nutrition & Health Report - {name}", size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Row([ft.Icon("bar_chart", color="#64B5F6"), ft.Text("Your Vitals", size=20, weight=ft.FontWeight.BOLD, color="white")], spacing=10),
                    vitals_container,
                    ft.Container(height=10),
                    ft.Row([ft.Icon("warning_amber", color="#FFB74D"), ft.Text("Health Alerts", size=20, weight=ft.FontWeight.BOLD, color="white")], spacing=10),
                    alerts_col,
                    diet_hint
                ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=20)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return ft.Text(f"Error loading dashboard: {e}", color="red", size=20)

        def build_doctor_dashboard():
            # State for this view
            view_state = {"mode": "list", "selected_pid": None} # modes: list, edit

            # --- 1. SEARCH & LIST VIEW ---
            search_box = ft.TextField(hint_text="Search by Name or ID...", expand=True)
            patient_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Name")),
                    ft.DataColumn(ft.Text("Hospital")),
                    ft.DataColumn(ft.Text("Last Report")),
                    ft.DataColumn(ft.Text("Action")),
                ],
                rows=[]
            )

            # --- 2. EDIT FORM CONTROLS ---
            # Define inputs
            f_pid = ft.TextField(label="Patient ID", read_only=True, width=100)
            f_name = ft.TextField(label="Name", expand=True)
            f_height = ft.TextField(label="Height (cm)", width=100)
            f_weight = ft.TextField(label="Weight (kg)", width=100)
            f_bp = ft.TextField(label="BP (mmHg)", width=100)
            f_sugar = ft.TextField(label="Sugar (mg/dL)", width=100)
            f_chol = ft.TextField(label="Cholesterol", width=100)
            f_hemo = ft.TextField(label="Hemoglobin", width=100)
            f_meds = ft.TextField(label="Medicines (One per line)", multiline=True, height=100)
            
            def load_patients(query=""):
                df = logic.get_all_patients_summary()
                if not df.empty:
                    if query:
                        df = df[df['Name'].astype(str).str.contains(query, case=False) | df['ID'].astype(str).str.contains(query)]
                    
                    rows = []
                    for _, row in df.iterrows():
                        rows.append(ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(row['ID']))),
                            ft.DataCell(ft.Text(row['Name'])),
                            ft.DataCell(ft.Text(str(row['Hospital']))),
                            ft.DataCell(ft.Text(str(row['Last Report']))),
                            ft.DataCell(ft.IconButton(icon="edit", on_click=lambda e, pid=row['ID']: open_edit_mode(pid))),
                        ]))
                    patient_table.rows = rows
                else:
                    patient_table.rows = []
                page.update()

            def search_change(e):
                load_patients(search_box.value)

            search_box.on_change = search_change

            container_list = ft.Column([
                ft.Text("Patient Database", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([search_box]),
                ft.Container(content=patient_table, border=ft.border.all(1, "#E0E0E0"), border_radius=10, expand=True, padding=10),
            ], expand=True)
            
            # --- EDIT LOGIC ---
            container_edit = ft.Column(visible=False, scroll=ft.ScrollMode.AUTO)

            def open_edit_mode(pid):
                view_state["selected_pid"] = pid
                # Fetch Data
                hist = logic.get_patient_history(pid)
                if not hist.empty:
                    rec = hist.iloc[-1]
                     # Fill Form
                    f_pid.value = str(pid)
                    f_name.value = rec.get('Patient_Name', '')
                    f_height.value = str(rec.get('Height', ''))
                    f_weight.value = str(rec.get('Weight', ''))
                    f_bp.value = str(rec.get('BP_Systolic', ''))
                    f_sugar.value = str(rec.get('Sugar_Fasting', ''))
                    f_chol.value = str(rec.get('Cholesterol_Total', ''))
                    f_hemo.value = str(rec.get('Hemoglobin', ''))
                    f_meds.value = rec.get('Medicines', '')

                # Switch Views
                container_list.visible = False
                container_edit.visible = True
                
                # Rebuild Edit Container content dynamically or just show it
                # We'll update the controls inside container_edit
                page.update()

            def save_record(e):
                try:
                    # Logic to save
                    pid = int(f_pid.value)
                    doc_id = int(str(user.get('Doctor_ID', 999))) # Fallback
                    hosp = user.get('Hospital_Name', 'General')
                    
                    # Analyze for auto-diet
                    bmi = logic.calculate_bmi(float(f_height.value or 0), float(f_weight.value or 0))
                    analysis_rt = logic.analyze_health({
                       'sugar': float(f_sugar.value or 0), 
                       'bp': int(f_bp.value or 0), 
                       'chol': float(f_chol.value or 0), 
                       'hemoglobin': float(f_hemo.value or 0), 
                       'bmi': bmi
                    })
                    
                    diet_note = f"Avoid: {', '.join(analysis_rt['avoid'])}\nEat: {', '.join(analysis_rt['boost'])}"

                    logic.save_patient_report(
                        pid, f_name.value, 
                        float(f_sugar.value or 0), float(f_chol.value or 0), int(f_bp.value or 0), float(f_hemo.value or 0),
                        float(f_height.value or 0), float(f_weight.value or 0), bmi,
                        doc_id, f_meds.value, hosp, diet_note
                    )
                    
                    ft.SnackBar(ft.Text("Record Saved Successfully!"), bgcolor="green").open = True
                    cancel_edit(None) # Go back
                except Exception as ex:
                    print(ex)
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error saving: {ex}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()

            def cancel_edit(e):
                container_edit.visible = False
                container_list.visible = True
                load_patients() # Refresh
                page.update()

            # Populate Edit Container
            container_edit.controls = [
                ft.Row([ft.IconButton("arrow_back", on_click=cancel_edit), ft.Text("Update Patient Record", size=24, weight=ft.FontWeight.BOLD)]),
                ft.Divider(),
                ft.Row([f_pid, f_name]),
                ft.Row([f_height, f_weight, f_bmi := ft.Text("BMI: -")]),
                ft.Row([f_bp, f_sugar, f_chol, f_hemo]),
                ft.Text("Prescription", weight=ft.FontWeight.BOLD),
                f_meds,
                ft.Row([
                    ft.ElevatedButton("Save Record", icon="save", on_click=save_record, bgcolor=primary_color, color="white"),
                    ft.OutlinedButton("Cancel", on_click=cancel_edit)
                ], alignment=ft.MainAxisAlignment.END)
            ]

            # Initial Load
            load_patients()
            
            return ft.Stack([container_list, container_edit])

        # --- LOAD INITIAL CONTENT ---
        if role == "Example": # Just for testing
             content_area.content = ft.Text("Example Role")
        elif role == "Patient":
             content_area.content = build_patient_dashboard()
        elif role == "Doctor":
             content_area.content = build_doctor_dashboard()
        else:
             content_area.content = ft.Text(f"Welcome {role}")

        # --- SIDEBAR LOGIC ---
        def build_chatbot_view():
            messages = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
            
            def add_message(role, text):
                align = ft.MainAxisAlignment.END if role == "user" else ft.MainAxisAlignment.START
                bg = "#BBDEFB" if role == "user" else "#FFFFFF"
                icon = "person" if role == "user" else "smart_toy"
                
                msg_bubble = ft.Row([
                    ft.Icon(icon, size=30, color=primary_color) if role == "bot" else ft.Container(),
                    ft.Container(
                        content=ft.Text(text, size=16),
                        padding=15,
                        bgcolor=bg,
                        border_radius=20,
                        width=None, # Auto width
                        constraints=ft.BoxConstraints(max_width=600)
                    ),
                    ft.Icon(icon, size=30, color=primary_color) if role == "user" else ft.Container(),
                ], alignment=align)
                
                messages.controls.append(msg_bubble)
                messages.controls.append(ft.Container(height=10)) # Spacer
                page.update()

            # Input field
            query_input = ft.TextField(hint_text="Ask about diet or recipes...", expand=True, border_radius=30, bgcolor="#FFFFFF")
            
            def send_click(e):
                text = query_input.value
                if not text: return
                
                add_message("user", text)
                query_input.value = ""
                page.update()
                
                # Get Bot Response
                # Retrieve Diagnosis for Context
                history = logic.get_patient_history(pid)
                diagnosis = []
                if not history.empty:
                    diagnosis = logic.analyze_health(history.iloc[-1])['diagnosis']
                
                reply = chatbot.get_response(text, diagnosis, "English")
                time.sleep(0.5) # Simulate thinking
                add_message("bot", reply)

            # Initial Greeting
            page.run_task(lambda: add_message("bot", chatbot.CHAT_TRANS["English"]["greeting"]))

            return ft.Column([
                ft.Text("🤖 AI Nutrition Assistant", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(content=messages, expand=True, bgcolor="#FAFAFA", padding=20, border_radius=10),
                ft.Row([query_input, ft.IconButton(icon="send", icon_color=primary_color, on_click=send_click)], alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True)

        def build_appointments_view():
            if role == "Patient":
                # Patient View: History + Request New
                appt_hist = logic.get_patient_appointments(pid)
                
                # History List
                hist_col = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)
                if not appt_hist.empty:
                    for _, r in appt_hist.iterrows():
                        icon = "hourglass_empty" if r['status'] == 'Requested' else "check_circle"
                        color = "#FF9800" if r['status'] == 'Requested' else "#4CAF50"
                        hist_col.controls.append(
                            ft.ListTile(
                                leading=ft.Icon(icon, color=color),
                                title=ft.Text(f"{r['date_requested']} - {r['status']}"),
                                subtitle=ft.Text(f"Note: {r['admin_message']}" if r['admin_message'] else "")
                            )
                        )
                else:
                    hist_col.controls.append(ft.Text("No history."))

                # Request Form
                hosp_dropdown = ft.Dropdown(label="Select Hospital", options=[], width=300)
                doc_dropdown = ft.Dropdown(label="Select Doctor", options=[], width=300, disabled=True)
                date_dropdown = ft.Dropdown(label="Select Date", options=[], width=300, disabled=True)
                
                # Load Hospitals
                hosps = logic.get_all_hospitals()
                hosp_dropdown.options = [ft.dropdown.Option(h) for h in hosps]

                def req_appt(e):
                    if not (doc_dropdown.value and date_dropdown.value):
                        return
                    doc_id = int(doc_dropdown.value)
                    date_val = date_dropdown.options[date_dropdown.options.index(ft.dropdown.Option(date_dropdown.value))].text # get text back if needed, but value is enough if unique
                    
                    logic.request_appointment(pid, name, doc_id, date_dropdown.value)
                    ft.SnackBar(ft.Text("Appointment Requested!"), bgcolor="#4CAF50").open = True
                    page.update()

                def on_hosp_change(e):
                    doc_dropdown.options = []
                    docs = logic.get_doctors_by_hospital(hosp_dropdown.value)
                    if not docs.empty:
                        doc_dropdown.options = [ft.dropdown.Option(str(row['id']), row['full_name']) for _, row in docs.iterrows()]
                        doc_dropdown.disabled = False
                    page.update()

                hosp_dropdown.on_change = on_hosp_change

                def on_doc_change(e):
                    date_dropdown.options = []
                    dates = logic.get_available_dates(int(doc_dropdown.value))
                    if dates:
                        date_dropdown.options = [ft.dropdown.Option(d) for d in dates]
                        date_dropdown.disabled = False
                    else:
                        date_dropdown.options = [ft.dropdown.Option("No dates available")]
                    page.update()

                doc_dropdown.on_change = on_doc_change

                return ft.Column([
                    ft.Text("My Appointments", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(content=hist_col, bgcolor="#FAFAFA", padding=10, border_radius=10),
                    ft.Divider(),
                    ft.Text("Request New Appointment", size=20, weight=ft.FontWeight.BOLD),
                    hosp_dropdown,
                    doc_dropdown,
                    date_dropdown,
                    ft.ElevatedButton("Request", on_click=req_appt, bgcolor=primary_color, color="#FFFFFF")
                ])

            elif role == "Doctor":
                doc_id = user.get('Doctor_ID')
                apps = logic.get_doc_appointments(doc_id)
                
                rows = []
                if not apps.empty:
                    for _, r in apps.iterrows():
                        rows.append(ft.DataRow(cells=[
                             ft.DataCell(ft.Text(r['patient_name'])),
                             ft.DataCell(ft.Text(r['date_requested'])),
                             ft.DataCell(ft.Text(r['status'])),
                        ]))
                
                table = ft.DataTable(columns=[ft.DataColumn(ft.Text("Patient")), ft.DataColumn(ft.Text("Date")), ft.DataColumn(ft.Text("Status"))], rows=rows)
                
                return ft.Column([
                    ft.Text("My Schedule", size=24, weight=ft.FontWeight.BOLD),
                    table
                ])

            return ft.Text("Admin / Other View")

        def build_admin_dashboard():
            # State
            # 1. Add Availability
            docs_df = logic.get_all_doctors()
            doc_opts = [ft.dropdown.Option(str(r['id']), f"{r['full_name']} ({r['hospital_name']})") for _, r in docs_df.iterrows()]
            
            sel_doc = ft.Dropdown(label="Select Doctor", options=doc_opts, width=400)
            sel_date = ft.TextField(label="Date (YYYY-MM-DD)", hint_text="2026-10-25", width=200) # Simple text input for now as DatePicker is complex to setup quickly
            
            def add_avail(e):
                if not (sel_doc.value and sel_date.value): return
                
                try:
                    d = datetime.datetime.strptime(sel_date.value, "%Y-%m-%d").date()
                    if logic.add_availability(int(sel_doc.value), d):
                         ft.SnackBar(ft.Text(f"Availability added for {d}"), bgcolor="#4CAF50").open = True
                    else:
                         ft.SnackBar(ft.Text("Date already exists."), bgcolor="#FF9800").open = True
                except ValueError:
                    ft.SnackBar(ft.Text("Invalid Date Format. Use YYYY-MM-DD"), bgcolor="#F44336").open = True
                page.update()

            # 2. Confirm Appointments
            pending = logic.get_pending_appointments()
            pending_col = ft.Column()
            
            def refresh_pending():
                pending = logic.get_pending_appointments()
                pending_col.controls.clear()
                if not pending.empty:
                    for _, r in pending.iterrows():
                        row_card = ft.Card(content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"Appt #{r['appt_id']}: {r['patient_name']} -> Doc {r['doc_id']}"),
                                ft.Text(f"Date: {r['date_requested']}"),
                                ft.Row([
                                    ft.ElevatedButton("Confirm", on_click=lambda e, aid=r['appt_id']: confirm_req(aid), bgcolor="#4CAF50", color="white")
                                ])
                            ]), padding=10
                        ))
                        pending_col.controls.append(row_card)
                else:
                    pending_col.controls.append(ft.Text("No pending requests."))
                page.update()

            def confirm_req(aid):
                logic.confirm_appointment(aid, "Confirmed by Admin.")
                refresh_pending()

            refresh_pending()

            return ft.Column([
                 ft.Text("Admin Dashboard", size=28, weight=ft.FontWeight.BOLD),
                 ft.Divider(),
                 ft.Text("Manage Doctor Availability", size=20, weight=ft.FontWeight.BOLD),
                 ft.Row([sel_doc, sel_date]),
                 ft.ElevatedButton("Add Availability", on_click=add_avail, bgcolor=primary_color, color="white"),
                 ft.Divider(),
                 ft.Text("Pending Appointment Requests", size=20, weight=ft.FontWeight.BOLD),
                 pending_col
            ], scroll=ft.ScrollMode.AUTO)

        # --- SIDEBAR LOGIC ---
        def on_nav_change(e):
            idx = e.control.selected_index
            if idx == 0:
                if role == "Patient": content_area.content = build_patient_dashboard()
                elif role == "Doctor": content_area.content = build_doctor_dashboard()
                elif role == "Admin": content_area.content = build_admin_dashboard()
            elif idx == 1:
                content_area.content = build_appointments_view()
            elif idx == 2:
                content_area.content = build_chatbot_view()
            elif idx == 3: # Logout
                user_state["logged_in"] = False
                user_state["user_info"] = None
                show_login()
                return
            page.update()

        # Initialize Default View (Dashboard)
        if role == "Patient": content_area.content = build_patient_dashboard()
        elif role == "Doctor": content_area.content = build_doctor_dashboard()
        elif role == "Admin": content_area.content = build_admin_dashboard()
        else: content_area.content = ft.Text(f"Welcome {role}. No dashboard view found.", color="white")

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            bgcolor="#111418",
            indicator_color="#263238",
            destinations=[
                ft.NavigationRailDestination(
                    icon="dashboard_outlined", 
                    selected_icon="dashboard", 
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon="calendar_month_outlined", 
                    selected_icon="calendar_month", 
                    label="Appts"
                ),
                ft.NavigationRailDestination(
                    icon="chat_bubble_outline", 
                    selected_icon="chat_bubble", 
                    label="AI Assistant"
                ),
                ft.NavigationRailDestination(
                    icon="logout", 
                    label="Logout"
                ),
            ],
            on_change=on_nav_change,
        )

        return ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1, color="#30363D"),
                content_area
            ],
            expand=True,
        )

    # --- ROUTING ---
    def show_login():
        page.clean()
        page.add(login_view())
        page.update()
    
    def show_dashboard():
        page.clean()
        page.bgcolor = "#111418" # Restore Dark Theme
        try:
            view = dashboard_view()
            page.add(view)
        except Exception as e:
            import traceback
            traceback.print_exc()
            page.add(ft.Column([
                ft.Text("CRITICAL ERROR", size=30, color="red"),
                ft.Text(str(e), color="red"),
            ]))
        page.update()

    # Start
    show_login()

if __name__ == "__main__":
    ft.app(target=main)
