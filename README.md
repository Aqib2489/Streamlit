# 📄 PDF Redactor & Pre-Processor

A Streamlit web application for automated PDF redaction and pre-processing. This tool extracts student IDs from assignment filenames, removes identification information from document headers, applies contrast enhancement, converts to grayscale, and provides batch processing with ZIP download.

---

## 🎯 Overview

This application automates the privacy-protection workflow for academic assignments by:
- **Batch processing** multiple PDF files simultaneously
- **Intelligent header redaction** using horizontal line detection
- **Filename-based ID extraction** (first 7 digits)
- **Image enhancement** (2x contrast, grayscale conversion)
- **ZIP export** for convenient download of all processed files

Built with **Streamlit** for a user-friendly web interface and **PyMuPDF** for high-quality PDF rendering.

### Key Features

✅ **Automated Header Redaction** - Detects horizontal lines and removes identification info  
✅ **Batch Processing** - Handle multiple PDFs with progress tracking  
✅ **Smart ID Extraction** - Uses filename's first 7 digits for anonymized output  
✅ **Image Enhancement** - 2x contrast boost + grayscale conversion  
✅ **High-Quality Output** - 200 DPI, 95% quality, optimized for readability  
✅ **ZIP Download** - Single-click download of all redacted PDFs  
✅ **Progress Tracking** - Real-time progress bar and file count display  

---

## 🏗️ Architecture

### Processing Pipeline

```
Upload PDFs → Extract Pages as Images → Detect Header Lines → 
Apply Black Redaction → Enhance Contrast → Convert to Grayscale → 
Generate PDF → Package as ZIP → Download
```

### Component Flow

```
┌─────────────────────────────────────────────────────┐
│         Streamlit Web Interface (app.py)            │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  File Uploader (Multiple PDFs)             │    │
│  └──────────────────┬─────────────────────────┘    │
│                     │                               │
│                     ▼                               │
│  ┌────────────────────────────────────────────┐    │
│  │  pdf_to_images() - PyMuPDF Conversion     │    │
│  │  • 2x zoom factor for high resolution     │    │
│  │  • RGB pixel extraction                   │    │
│  │  • Page-by-page processing                │    │
│  └──────────────────┬─────────────────────────┘    │
│                     │                               │
│                     ▼                               │
│  ┌────────────────────────────────────────────┐    │
│  │  redact_ids_from_filename()                │    │
│  │  • Convert to grayscale for line detection│    │
│  │  • Horizontal line scanning (>50% width)  │    │
│  │  • Dynamic black fill height calculation  │    │
│  │  • 2x contrast enhancement                │    │
│  └──────────────────┬─────────────────────────┘    │
│                     │                               │
│                     ▼                               │
│  ┌────────────────────────────────────────────┐    │
│  │  images_to_pdf() - PDF Generation          │    │
│  │  • 200 DPI resolution                      │    │
│  │  • 95% quality compression                 │    │
│  │  • Multi-page PDF assembly                 │    │
│  └──────────────────┬─────────────────────────┘    │
│                     │                               │
│                     ▼                               │
│  ┌────────────────────────────────────────────┐    │
│  │  ZIP Packaging & Download                  │    │
│  │  • Filename: first_7_digits.pdf            │    │
│  │  • In-memory ZIP creation                  │    │
│  │  • Download button with progress           │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | Streamlit | Interactive file upload & download interface |
| **PDF Rendering** | PyMuPDF (fitz) | High-quality PDF to image conversion |
| **Image Processing** | Pillow (PIL) | Redaction, contrast enhancement, format conversion |
| **Numerical Operations** | NumPy | Pixel analysis for line detection |
| **File Compression** | zipfile | Batch packaging of redacted PDFs |

---

## 📁 Project Structure

```
Streamlit/
│
├── app.py                  # Main application (111 lines)
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
│
└── .git/                  # Git version control
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Step 1: Clone Repository

```bash
git clone https://github.com/Aqib2489/Streamlit.git
cd Streamlit
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Libraries:**
```
streamlit              # Web application framework
pymupdf               # PDF rendering (fitz library)
Pillow                # Image processing
numpy                 # Array operations for pixel analysis
opencv-python-headless # Image processing utilities
PyPDF2                # Additional PDF manipulation
```

### Step 3: Run Application

```bash
streamlit run app.py
```

The application opens in your browser at `http://localhost:8501`

---

## 💻 Usage Guide

### Basic Workflow

1. **Upload PDFs:**
   - Click "Browse files" or drag-and-drop
   - Select multiple PDF files (assignment submissions)
   - Files should follow naming convention: `1234567_Name_Assignment.pdf`

2. **Start Redaction:**
   - Click "Start Redaction" button
   - Progress bar shows processing status
   - Each file displays completion count (e.g., "5/20 PDFs redacted")

3. **Download Results:**
   - Click "Download all redacted PDFs as a ZIP file"
   - ZIP filename: `all_redacted_pdfs.zip`
   - Individual PDFs named: `1234567.pdf` (first 7 digits from original filename)

### Example Use Case

**Original Files:**
```
2301456_John_Smith_Assignment1.pdf
2301789_Jane_Doe_Assignment1.pdf
2302034_Bob_Lee_Assignment1.pdf
```

**Processing:**
- Removes header identification (name, ID visible in document)
- Enhances contrast for better readability
- Converts to grayscale

**Output (in ZIP):**
```
2301456.pdf
2301789.pdf
2302034.pdf
```

---

## 🔍 Technical Deep Dive

### 1. PDF to Image Conversion

**Function:** `pdf_to_images(uploaded_pdf, zoom=2.0)`

**How it works:**
```python
mat = fitz.Matrix(zoom, zoom)  # 2x zoom = 144 DPI (72 * 2)
pix = doc[page_num].get_pixmap(matrix=mat)
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
```

**Parameters:**
- `zoom=2.0` → 144 DPI resolution (sufficient for readability)
- RGB color mode for initial extraction
- Page-by-page processing to manage memory

**Output:** List of PIL Image objects

---

### 2. Header Redaction Algorithm

**Function:** `redact_ids_from_filename(images)`

**Step-by-Step Process:**

#### Step 1: Horizontal Line Detection
```python
img_gray = img.convert("L")  # Grayscale for line detection
img_np = np.array(img_gray)

for y in range(img_height):
    if np.sum(img_np[y] < 128) > img_width * 0.5:
        line_position = y
        break
```
- **Logic:** Scans each row of pixels
- **Threshold:** Row with >50% dark pixels (< 128 value) = horizontal line
- **Purpose:** Identifies separator between header and content

#### Step 2: Dynamic Black Fill Height
```python
black_fill_height = img_height // 10 if line_position > img_height * 0.15 else line_position
```
- **Case A:** Line found below 15% height → Fill 10% of page (conservative)
- **Case B:** Line found in top 15% → Fill up to line position
- **Rationale:** Adapts to different document formats

#### Step 3: Redaction Application
```python
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, img_width, black_fill_height], fill="black")
```
- **Rectangle:** From top-left corner to calculated height
- **Color:** Solid black (RGB: 0, 0, 0)

#### Step 4: Enhancement
```python
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)  # 2x contrast
img = img.convert("L")       # Grayscale
```
- **Contrast:** 2x boost for better text clarity
- **Grayscale:** Reduces file size, improves readability

---

### 3. PDF Generation

**Function:** `images_to_pdf(images)`

**Specifications:**
```python
images[0].save(
    pdf_buffer, 
    format="PDF", 
    save_all=True,           # Multi-page PDF
    append_images=images[1:], # Additional pages
    quality=95,              # High quality (1-100 scale)
    dpi=(200, 200)          # 200 DPI resolution
)
```

**Quality Trade-offs:**
- **DPI:** 200 (good balance between file size & readability)
- **Quality:** 95% (minimal compression artifacts)
- **Format:** PDF/A-compatible for archival

---

### 4. Batch Processing & ZIP Export

**Implementation:**
```python
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
    for index, uploaded_file in enumerate(uploaded_files):
        first_seven_digits = base_name[:7]  # Extract ID from filename
        pdf_buffer = images_to_pdf(redacted_images)
        zip_file.writestr(f"{first_seven_digits}.pdf", pdf_buffer.read())
        progress_bar.progress((index + 1) / total_files)
```

**Features:**
- **In-memory processing:** No temporary files on disk
- **Progress tracking:** Real-time update for each file
- **Compression:** ZIP_DEFLATED for smaller download size
- **Naming:** First 7 characters from original filename

---

## 🎨 Customization

### Adjust Redaction Height

**Conservative (more redaction):**
```python
black_fill_height = img_height // 8  # Fill 12.5% instead of 10%
```

**Aggressive (less redaction):**
```python
black_fill_height = img_height // 15  # Fill 6.7% instead of 10%
```

### Change Line Detection Threshold

**More sensitive (detect thinner lines):**
```python
if np.sum(img_np[y] < 128) > img_width * 0.3:  # 30% instead of 50%
```

**Less sensitive (only thick lines):**
```python
if np.sum(img_np[y] < 128) > img_width * 0.7:  # 70% instead of 50%
```

### Modify Contrast Enhancement

```python
img = enhancer.enhance(1.5)  # Subtle enhancement
img = enhancer.enhance(3.0)  # Aggressive enhancement
```

### Change Output Resolution

```python
zoom = 1.5  # Lower resolution (108 DPI) - smaller files
zoom = 3.0  # Higher resolution (216 DPI) - larger files
```

### Customize ZIP Filename

```python
st.download_button(
    label="Download Redacted PDFs",
    data=zip_buffer,
    file_name="redacted_assignments_batch_1.zip",  # Custom name
    mime="application/zip"
)
```

---

### Scalability Considerations

**Current Design:** Desktop web app for small-to-medium batches  
**For Large-Scale:**
- Implement queue-based processing (Celery, RQ)
- Add cloud storage (AWS S3, Google Cloud Storage)
- Use containerization (Docker) for deployment
- Add database for tracking job status
- Implement email notification for completed batches

---


## 👤 Author

**Mohammad Aqib**  
- **Email:** maqib@ualberta.ca  
- **Institution:** University of Alberta  
- **GitHub:** [Aqib2489](https://github.com/Aqib2489)

---

## 📄 License

This project is open-source and available for educational and commercial use.

---

## 🙏 Acknowledgments

- **PyMuPDF (fitz)** - For high-quality PDF rendering
- **Streamlit Team** - For the amazing web framework
- **Pillow Community** - For powerful image processing tools
- **NumPy** - For efficient array operations

---

## 📞 Support

For issues or questions:
- Review the Troubleshooting section above
- Check [Streamlit Documentation](https://docs.streamlit.io/)
- Check [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- Contact: maqib@ualberta.ca

---

