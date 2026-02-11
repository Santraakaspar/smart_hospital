import app
import logic
import os

# Mock data
vitals = {'Sugar_Fasting': 150, 'BP_Systolic': 130, 'BMI': 26, 'Weight': 80, 'Cholesterol_Total': 210, 'Hemoglobin': 11}
analysis = logic.analyze_health(vitals)
doctor_note = "Please take care."
medicines = "Metformin 500mg"

languages = ["Malayalam", "Telugu"]

try:
    for lang in languages:
        print(f"Testing PDF generation for {lang}...")
        pdf_bytes = app.generate_pdf_report(
            patient_name="Test Patient",
            doctor_name="Dr. Test",
            hospital_name="Test Hospital",
            vitals=vitals,
            analysis=analysis,
            recipes=[],
            language=lang,
            doctor_note=doctor_note,
            medicines=medicines
        )
        if pdf_bytes:
            print(f"SUCCESS: Generated PDF for {lang} ({len(pdf_bytes)} bytes)")
        else:
            print(f"FAILURE: No PDF generated for {lang}")

except Exception as e:
    print(f"ERROR: {e}")
