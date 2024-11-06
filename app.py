import streamlit as st
import fitz  # PyMuPDF
import os
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np
import zipfile
import io

# Step 1: Extract pages as images
def pdf_to_images(input_pdf_path, zoom=2.0):
    doc = fitz.open(input_pdf_path)
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

def images_to_pdf(images, output_pdf_path, dpi=200):
    images[0].save(
        output_pdf_path, 
        save_all=True, 
        append_images=images[1:], 
        quality=95, 
        dpi=(dpi, dpi)
    )

# Streamlit interface
st.title("Batch PDF Redactor")
input_folder = st.text_input("Enter the path to the input folder containing PDF files:")
output_folder = st.text_input("Enter the path to the output folder for saving redacted PDFs:")

if st.button("Start Redaction") and input_folder and output_folder:
    os.makedirs(output_folder, exist_ok=True)
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    if pdf_files:
        st.write(f"Found {len(pdf_files)} PDF files in the input folder.")
        
        # Progress bar
        progress_bar = st.progress(0)  # Initial progress bar
        total_files = len(pdf_files)
        
        for i, pdf_file in enumerate(pdf_files):
            input_pdf = os.path.join(input_folder, pdf_file)
            base_name = os.path.basename(pdf_file)
            first_seven_digits = base_name[:7]
            output_pdf = os.path.join(output_folder, f"{first_seven_digits}.pdf")
            
            images = pdf_to_images(input_pdf)
            redacted_images = redact_ids_from_filename(images)
            images_to_pdf(redacted_images, output_pdf, dpi=200)
            
            # Update progress
            progress_bar.progress((i + 1) / total_files)
            
            # Show current progress text
            st.write(f"Processed {i + 1}/{total_files} PDFs: {output_pdf}")
            
        st.write("All PDFs have been processed.")
    else:
        st.write("No PDF files found in the specified input folder.")
