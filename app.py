import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np
from io import BytesIO
import os

# Step 1: Extract pages as images
def pdf_to_images(uploaded_pdf, zoom=2.0):
    pdf_bytes = uploaded_pdf.read()  # Read the file content as bytes
    doc = fitz.open("pdf", pdf_bytes)
    images = []
    mat = fitz.Matrix(zoom, zoom)  # Adjust the zoom factor as needed
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images

def redact_ids_from_filename(images):
    redacted_images = []
    for img in images:
        img_gray = img.convert("L")
        img_np = np.array(img_gray)
        img_height, img_width = img_np.shape

        # Step 1: Find the first horizontal line
        line_position = None
        for y in range(img_height):
            if np.sum(img_np[y] < 128) > img_width * 0.5:
                line_position = y
                break

        if line_position is None:
            line_position = img_height

        # Step 2: Determine the black fill height
        black_fill_height = img_height // 10 if line_position > img_height * 0.15 else line_position

        # Step 3: Apply black fill
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, img_width, black_fill_height], fill="black")

        # Increase the contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)  # Increase the contrast factor as needed

        # Convert to grayscale
        img = img.convert("L")

        redacted_images.append(img)
    return redacted_images

def images_to_pdf(images):
    pdf_buffer = BytesIO()
    images[0].save(
        pdf_buffer, 
        format="PDF", 
        save_all=True, 
        append_images=images[1:], 
        quality=95, 
        dpi=(200, 200)
    )
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit interface
st.title("Batch PDF Redactor with File Upload")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if st.button("Start Redaction") and uploaded_files:
    for uploaded_file in uploaded_files:
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # Convert PDF to images
        images = pdf_to_images(uploaded_file)
        
        # Redact images
        redacted_images = redact_ids_from_filename(images)
        
        # Save the redacted images to an in-memory PDF
        pdf_buffer = images_to_pdf(redacted_images)
        
        # Provide download link for the redacted PDF
        st.download_button(
            label=f"Download redacted PDF: {base_name}",
            data=pdf_buffer,
            file_name=f"{base_name}_redacted.pdf",
            mime="application/pdf"
        )
