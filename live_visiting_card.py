import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
import os

address_line1 = "502- 5th Floor, I-Square Corporate Park,"
address_line2 = " Science City Rd, near CIMS Hospital,"
address_line3 = "Panchamrut Bunglows II, Sola, Ahmedabad, Gujarat 380060."


# Function to create the visiting card
def create_visiting_card(firstname, role, email, contact_number, output_pdf_path):
    # Paths to the input PDF and custom fonts
    input_pdf_path = "Visiting_Card_New.pdf"
    pdfmetrics.registerFont(TTFont("Gilroy-Regular", "./gilroy/Gilroy-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Gilroy-Heavy", "./gilroy/Gilroy-Heavy.ttf"))

    # Load the input PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Get the second page dimensions
    second_page = reader.pages[1]
    page_width = float(second_page.mediabox.width)
    page_height = float(second_page.mediabox.height)

    # Create a buffer for overlay
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Split the name if needed
    def split_name(name, max_length):
        if len(name) <= max_length:
            return name, ""
        split_pos = name.rfind(" ", 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        return name[:split_pos].strip(), name[split_pos:].strip()

    first_part, second_part = split_name(firstname, 15)

    # Draw on canvas
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

    # Email: Regular, medium size (with hex color)
    can.setFont("Gilroy-Regular", 6)  # Normal font size 8
    can.setFillColor(HexColor("#000000"))  # Black color in hex
    can.drawString(40, page_height - 100, address_line1)  # Position for email

    # Email: Regular, medium size (with hex color)
    can.setFont("Gilroy-Regular", 6)  # Normal font size 8
    can.setFillColor(HexColor("#000000"))  # Black color in hex
    can.drawString(38, page_height - 107, address_line2)  # Position for email

    # Email: Regular, medium size (with hex color)
    can.setFont("Gilroy-Regular", 6)  # Normal font size 8
    can.setFillColor(HexColor("#000000"))  # Black color in hex
    can.drawString(40, page_height - 114, address_line3)  # Position for email

    # Save and merge overlay
    can.save()
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    overlay_page = overlay_pdf.pages[0]
    second_page.merge_page(overlay_page)
    writer.add_page(reader.pages[0])
    writer.add_page(second_page)
    for i in range(2, len(reader.pages)):
        writer.add_page(reader.pages[i])

    # Write to output
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

    return output_pdf_path


# Streamlit UI
st.set_page_config(page_title="Visiting Card Generator", layout="centered")

st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🖋️ Visiting Card Generator")
st.write("Fill out the details below to create your professional visiting card!")

# Input form
with st.form("visiting_card_form"):
    firstname = st.text_input("Full Name", value="Harshil Sarariya")
    role = st.text_input("Role", value="BUSINESS DEVELOPMENT MANAGER")
    email = st.text_input("Email", value="harshilsarariya@egniol.in")
    contact_number = st.text_input("Contact Number", value="+91 9510142642")
    submitted = st.form_submit_button("Generate Visiting Card")

if submitted:
    output_pdf_path = f"{firstname.replace(' ', '_')}_visiting_card.pdf"
    create_visiting_card(firstname, role, email, contact_number, output_pdf_path)
    st.success("Your visiting card has been generated! 🎉")
    with open(output_pdf_path, "rb") as file:
        st.download_button(
            label="Download Visiting Card",
            data=file,
            file_name=output_pdf_path,
            mime="application/pdf",
        )

    os.remove(output_pdf_path)
