from flask import Flask, render_template, request, send_file
import os
from fpdf import FPDF

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SECTIONS = {
    "general": "Summary",
    "maintenance" : "Maintenance Work",
    "projects" : "Recommendations Require Approval",
    "keys" : "Locks",
    "smoking" : "Signs of Smoking",
    "pets" : "Signs of Pets", 
    "appliances": "Appliances",
    "plumbing": "Plumbing",
    "electrical": "Electrical",
    "detectors" : "Detectors",
    "hvac": "HVAC System",
    "shutoff" : "Water Shutoff",
    "doors_windows": "Doors & Windows",
    "steps_handrails" : "Steps & Handrails",
    "garage" : "Garage Doors",
    "condenser" : "AC Condenser",
    "other" : "Other"
}

def parse_inspection(text):
    text = text.lower()

    report = {label: {"notes": [], "images": []} for label in SECTIONS.values()}

    parts = [p.strip() for p in text.replace(",", ".").split(".") if p.strip()]

    for p in parts:
        if "overall" in p:
            report["Summary"]["notes"].append(p)
        elif    "fixed" in p:
            report["Maintenance Work"]["notes"].append(p)
        elif    "recommend" in p:
            report["Recommendations Require Approval"]["notes"].append(p)
        elif    "key" in p:
            report["Locks"]["notes"].append(p) 
        elif    "smoking" in p:
            report["Signs of Smoking"]["notes"].append(p)        
        elif    "dog" in p:
            report["Signs of Pets"]["notes"].append(p)
        elif "appliance" in p or "water shutoff" in p:
            report["Appliances"]["notes"].append(p)
        elif "plumbing" in p or "water shutoff" in p:
            report["Plumbing"]["notes"].append(p)
        elif "electrical" in p or "detector" in p:
            report["Electrical"]["notes"].append(p)
        elif "detector" in p or "detector" in p:
            report["Detectors"]["notes"].append(p),
        elif "furnace" in p or "ac" in p or "filter" in p:
            report["HVAC System"]["notes"].append(p)
        elif "shutoff" in p or "ac" in p or "filter" in p:
            report["Water Shutoff"]["notes"].append(p)
        elif "window" in p or "door" in p:
            report["Doors & Windows"]["notes"].append(p)
        elif "steps" in p or "door" in p:
            report["Steps & Handrails"]["notes"].append(p)
        elif "garage" in p or "door" in p:
            report["Garage Doors"]["notes"].append(p)
        elif "condenser" in p or "door" in p:
            report[""AC Condenser]["notes"].append(p)
        else:
            report["Other"]["notes"].append(p)

    return report


@app.route("/", methods=["GET", "POST"])

def index():
    if request.method == "POST":
        try:
            print("FORM:", request.form)
            text = request.form.get("inspection_text", "")
            print(text)
            report = parse_inspection(text)
        except Exception as e:
            return f"ERROR: {str(e)}", 500

        # Handle uploads
        #for section in SECTIONS:
         #   files = request.files.getlist(section) if section in request.files else []
          #  for key, label in SECTIONS.items():
           #     files = request.files.getlist(key)

            #    for file in files:
             #       if file and file.filename:
              #          path = os.path.join(UPLOAD_FOLDER, file.filename)
               #         file.save(path)
                #        report[label]["images"].append(path)

        # Generate PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Property Inspection Report", ln=True)

        for section, content in report.items():
        # Skip empty sections
            if not content["notes"] and not content.get("images"):
                continue

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, section, ln=True)

            pdf.set_font("Arial", "", 10)

            for note in content["notes"]:
                pdf.multi_cell(0, 8, f"- {note}")

        pdf_path = "report.pdf"
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)

    return render_template("index.html", sections=SECTIONS)


if __name__ == "__main__":
    app.run()
