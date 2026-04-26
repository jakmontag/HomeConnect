from flask import Flask, render_template, request, send_file
import os
from fpdf import FPDF

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SECTIONS = {
    "general": "General Condition",
    "appliances": "Appliances",
    "plumbing": "Plumbing",
    "electrical": "Electrical",
    "hvac": "HVAC System",
    "doors_windows": "Doors & Windows"
}

def parse_inspection(text):
    text = text.lower()
    report = {s: {"notes": [] } for s in SECTIONS}

    parts = [p.strip() for p in text.replace(",", ".").split(".") if p.strip()]

    for p in parts:
        if "appliance" in p:
            report["Appliances"]["notes"].append(p)
        elif "plumbing" in p or "water shutoff" in p:
            report["Plumbing"]["notes"].append(p)
        elif "electrical" in p or "detector" in p:
            report["Electrical"]["notes"].append(p)
        elif "furnace" in p or "ac" in p or "filter" in p:
            report["HVAC System"]["notes"].append(p)
        elif "window" in p or "door" in p:
            report["Doors & Windows"]["notes"].append(p)
        else:
            report["General Condition"]["notes"].append(p)

    return report


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
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
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, section, ln=True)

            pdf.set_font("Arial", "", 10)
            for note in content["notes"]:
                pdf.multi_cell(0, 8, f"- {note}")

            for img in content["images"]:
                try:
                    pdf.image(img, w=100)
                except:
                    pass

        pdf_path = "report.pdf"
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)

    return render_template("index.html", sections=SECTIONS)


if __name__ == "__main__":
    app.run
