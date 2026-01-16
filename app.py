import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
import io

# Page Config
st.set_page_config(
    page_title="PDF Vibe Watermarker",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Vibe (Light Blue/White) ---
st.markdown("""
<style>
    .stApp {
        background-color: #F8FDFF; /* Very light blue background */
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        background: linear-gradient(45deg, #2196F3, #00BCD4); /* Blue gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    h2, h3 {
        color: #0D47A1 !important; /* Dark Blue headers */
    }
    .stButton>button {
        width: 100%;
        background-color: #2196F3; /* Material Blue */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1976D2; /* Darker Blue on hover */
        border: none;
        transform: scale(1.02);
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #B3E5FC; /* Light Blue Border */
        background-color: #E1F5FE;
        border-radius: 10px;
        padding: 1rem;
    }
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E1F5FE;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ PDF Vibe Watermarker")
st.markdown("Add professional image watermarks to your PDFs in seconds.")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🎨 Watermark Settings")
    
    # Placeholders for controls
    opacity = st.slider("Opacity", 0.1, 1.0, 0.5)
    scale = st.slider("Scale", 0.1, 2.0, 0.3)
    rotation = st.slider("Rotation (degrees)", 0, 360, 0)
    
    st.subheader("📍 Position")
    alignment = st.selectbox("Preset Location", ["Center", "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"])
    
    x_offset = st.slider("Horizontal Fine-tune", -500, 500, 0)
    y_offset = st.slider("Vertical Fine-tune", -500, 500, 0)

# --- Main Content ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Source PDF")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

with col2:
    st.subheader("2. Upload Watermark")
    img_file = st.file_uploader("Upload Image (PNG/JPG)", type=["png", "jpg", "jpeg"])


# --- Logic Imported from Module ---
from watermarker import process_image, add_watermark

if pdf_file and img_file:
    # 1. Process Watermark Image
    processed_img_bytes, img_size = process_image(img_file, opacity, rotation)
    
    # 2. Show Preview
    st.subheader("👁️ Live Preview (Page 1)")
    
    # Use a spinner for "vibe" but keeps it fast
    # with st.spinner("Generating preview..."):
    preview_img = add_watermark(pdf_file, processed_img_bytes, img_size, scale, alignment, x_offset, y_offset, "Preview", "", is_preview=True)
    
    st.image(preview_img, caption="Preview of Watermark on Page 1", use_container_width=True)
    
    # 3. Download Options
    st.divider()
    st.header("🚀 Process & Download")
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        pages_choice = st.radio("Apply to:", ["All Pages", "First Page Only", "Custom Range"])
    with col_opt2:
        custom_range_input = ""
        if pages_choice == "Custom Range":
            custom_range_input = st.text_input("Page Range (e.g., 1-5, 8)", "1")

    if st.button("Apply Watermark to File"):
        with st.spinner("Processing PDF..."):
            final_pdf = add_watermark(pdf_file, processed_img_bytes, img_size, scale, alignment, x_offset, y_offset, pages_choice, custom_range_input, is_preview=False)
        
        st.success("Done!")
        
        # Determine output filename
        original_name = pdf_file.name
        if original_name.lower().endswith(".pdf"):
            base_name = original_name[:-4]
        else:
            base_name = original_name
        output_filename = f"{base_name}_watermarked.pdf"

        st.download_button(
            label="Download Watermarked PDF",
            data=final_pdf,
            file_name=output_filename,
            mime="application/pdf"
        )
else:
    st.info("👆 Upload your files to get started!")
