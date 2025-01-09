from flask import Flask, request, render_template, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
import csv
from datetime import datetime
import os


def log_submission(data):
    """
    Logs the form submission to a CSV file with date and time.

    Args:
        data (dict): A dictionary containing user information (name, role, email, contact number).
    """
    log_file = "submissions_log.csv"  # Name of the CSV file
    headers = ["Full Name", "Role", "Email", "Contact Number", "Submission Time"]

    # Add current timestamp
    data["Submission Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Write the log entry to the CSV file
    try:
        with open(log_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            # If file is empty, write the headers first
            if file.tell() == 0:
                writer.writeheader()

            writer.writerow(data)
        print("Log entry added successfully.")
    except Exception as e:
        print(f"Error writing to log file: {e}")


app = Flask(__name__)

# Predefined address
address_line1 = "502- 5th Floor, I-Square Corporate Park,"
address_line2 = "Science City Rd, near CIMS Hospital,"
address_line3 = "Panchamrut Bunglows II, Sola, Ahmedabad, Gujarat 380060."


# Function to create the visiting card
def create_visiting_card(firstname, role, email, contact_number, output_pdf_path):
    input_pdf_path = "Visiting_Card_New.pdf"  # Ensure this file exists
    pdfmetrics.registerFont(TTFont("Gilroy-Regular", "./gilroy/Gilroy-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Gilroy-Heavy", "./gilroy/Gilroy-Heavy.ttf"))

    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    second_page = reader.pages[1]
    page_width = float(second_page.mediabox.width)
    page_height = float(second_page.mediabox.height)

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Split name for long names
    def split_name(name, max_length):
        if len(name) <= max_length:
            return name, ""
        split_pos = name.rfind(" ", 0, max_length)
        return (
            (name[:split_pos].strip(), name[split_pos:].strip())
            if split_pos != -1
            else (name[:max_length], name[max_length:])
        )

    first_part, second_part = split_name(firstname, 15)
    can.setFont("Gilroy-Heavy", 14)
    can.setFillColor(HexColor("#ef4028"))
    can.drawString(28, page_height - 32, first_part)
    if second_part:
        can.drawString(28, page_height - 44, second_part)

    can.setFont("Gilroy-Regular", 8)
    can.setFillColor(HexColor("#000000"))
    can.drawString(28, page_height - 52 if second_part else page_height - 44, role)
    can.setFont("Gilroy-Regular", 7)
    can.drawString(40, page_height - 65, contact_number)
    can.drawString(40, page_height - 80, email)

    can.setFont("Gilroy-Regular", 6)
    can.setFillColor(HexColor("#000000"))
    can.drawString(40, page_height - 100, address_line1)
    can.drawString(40, page_height - 107, address_line2)
    can.drawString(40, page_height - 114, address_line3)

    can.save()
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    overlay_page = overlay_pdf.pages[0]
    second_page.merge_page(overlay_page)
    writer.add_page(reader.pages[0])
    writer.add_page(second_page)
    for i in range(2, len(reader.pages)):
        writer.add_page(reader.pages[i])

    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

    return output_pdf_path


# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        role = request.form.get("role")
        email = request.form.get("email")
        contact_number = request.form.get("contact_number")

        user_data = {
            "Full Name": firstname,
            "Role": role,
            "Email": email,
            "Contact Number": contact_number,
        }

        log_submission(user_data)

        output_pdf_path = f"{firstname.replace(' ', '_')}_visiting_card.pdf"
        create_visiting_card(firstname, role, email, contact_number, output_pdf_path)

        try:
            # Send file to user
            response = send_file(
                output_pdf_path, as_attachment=True, download_name=output_pdf_path
            )
            os.remove(output_pdf_path)

            return response
        except Exception as e:
            if os.path.exists(output_pdf_path):
                os.remove(output_pdf_path)  # Ensure cleanup in case of errors
            return f"An error occurred: {str(e)}", 500

    return render_template("index.html")


# HTML Template (index.html)
@app.route("/template")
def template():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visiting Card Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }

        body {
            background: #f4f4f9;
            color: #333;
            min-height: 100vh;
        }

        .navbar {
            background: #2c3e50;
            padding: 1rem 2rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }

        .logo {
            color: #fff;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
        }

        .main-content {
            padding-top: 80px;
            min-height: calc(100vh - 60px);
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 600px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin: 2rem;
        }

        h1 {
            font-size: 24px;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .form-group {
            margin-bottom: 1.2rem;
        }

        label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }

        input {
            width: 100%;
            padding: 0.8rem;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }

        input:focus {
            outline: none;
            border-color: #2c3e50;
        }

        button {
            width: 100%;
            padding: 1rem;
            background-color: #2c3e50;
            color: #fff;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-top: 1rem;
        }

        button:hover {
            background-color: #34495e;
        }

        footer {
            text-align: center;
            font-size: 12px;
            color: #777;
            margin-top: 1.5rem;
            padding-bottom: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">QRT - EGNIOL</a>
    </nav>
    
    <div class="main-content">
        <div class="container">
            <h1>Generate Your Visiting Card</h1>
            <form method="post" action="/">
                <div class="form-group">
                    <label for="firstname">Full Name</label>
                    <input type="text" id="firstname" name="firstname" placeholder="Enter your full name" required>
                </div>
                
                <div class="form-group">
                    <label for="role">Role</label>
                    <input type="text" id="role" name="role" placeholder="Enter your role or title" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" placeholder="Enter your email address" required>
                </div>
                
                <div class="form-group">
                    <label for="contact_number">Contact Number</label>
                    <input type="text" id="contact_number" name="contact_number" placeholder="Enter your contact number" required>
                </div>
                
                <button type="submit">Generate Visiting Card</button>
            </form>
            <footer>
                &copy; 2025 EGNIOL. All rights reserved.
            </footer>
        </div>
    </div>
</body>
</html>
    """


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
