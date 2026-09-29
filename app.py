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
    st.header("🛠️ Navigation")
    mode = st.radio("Choose Tool", ["Watermark PDF", "Merge PDFs", "Reorder Pages"], index=0)
    
    st.divider()

    if mode == "Watermark PDF":
        st.header("🎨 Settings")
        
        # Placeholders for controls
        opacity = st.slider("Opacity", 0.1, 1.0, 0.5)
        scale = st.slider("Scale", 0.1, 2.0, 0.3)
        rotation = st.slider("Rotation (degrees)", 0, 360, 0)
        
        st.subheader("📍 Position")
        alignment = st.selectbox("Preset Location", ["Center", "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"])
        
        x_offset = st.slider("Horizontal Fine-tune", -500, 500, 0)
        y_offset = st.slider("Vertical Fine-tune", -500, 500, 0)

# --- Logic Imported from Module ---
from watermarker import process_image, add_watermark
from pdf_tools import merge_pdfs, reorder_pdf, get_pdf_previews

# ==========================================
# MODE: WATERMARK PDF
# ==========================================
if mode == "Watermark PDF":
    st.header("✨ Watermark PDF")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Upload Source PDF")
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    with col2:
        st.subheader("2. Upload Watermark")
        img_file = st.file_uploader("Upload Image (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    if pdf_file and img_file:
        # 1. Process Watermark Image
        processed_img_bytes, img_size = process_image(img_file, opacity, rotation)
        
        # 2. Show Preview
        st.subheader("👁️ Live Preview (Page 1)")
        
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

# ==========================================
# MODE: MERGE PDFS
# ==========================================
elif mode == "Merge PDFs":
    st.header("🔗 Merge PDFs & Images")
    st.write("Combine up to 10 files (PDFs or Images) into a single PDF document.")
    
    uploaded_files = st.file_uploader("Upload files (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("⚠️ Maximum 10 files allowed.")
        else:
            st.write(f"selected {len(uploaded_files)} files.")
            
            # List them to show order
            st.subheader("Proposed Order:")
            for i, f in enumerate(uploaded_files):
                st.text(f"{i+1}. {f.name}")
            st.caption("Note: Streamlit processes files in the order you selected them (or alphabetical if drag-dropped).")
                
            if st.button("Merge Files"):
                with st.spinner("Merging..."):
                    merged_pdf = merge_pdfs(uploaded_files)
                
                st.success("Merged successfully!")
                
                st.download_button(
                    label="Download Merged PDF",
                    data=merged_pdf,
                    file_name="merged_document.pdf",
                    mime="application/pdf"
                )

# ==========================================
# MODE: REORDER PAGES
# ==========================================
elif mode == "Reorder Pages":
    st.header("glider Reorder PDF Pages")
    st.write("Upload a PDF to rearrange its pages.")
    
    pdf_file = st.file_uploader("Upload PDF to Reorder", type=["pdf"])
    
    if pdf_file:
        try:
            # Generate Previews
            with st.spinner("Generating thumbnails..."):
                previews = get_pdf_previews(pdf_file)
            
            num_pages = len(previews)
            st.write(f"Document has **{num_pages}** pages.")
            
            # Show Thumbnails in a Grid
            st.subheader("📄 Page Gallery")
            cols = st.columns(min(4, num_pages) if num_pages > 0 else 1)
            
            for i, img in enumerate(previews):
                col_idx = i % 4
                with cols[col_idx]:
                    st.image(img, caption=f"Page {i+1}", use_container_width=True)
            
            st.divider()
            
            # Reorder Interface
            st.subheader("📝 Select New Order")
            st.markdown("Select pages in the order you want them to appear in the new PDF.")
            
            page_options = [f"Page {i+1}" for i in range(num_pages)]
            
            # Helpers to pre-fill
            col_h1, col_h2 = st.columns([1,4])
            with col_h1:
                if st.button("Select All"):
                    st.session_state['reorder_selection'] = page_options
            with col_h2:
                if st.button("Clear Selection"):
                    st.session_state['reorder_selection'] = []

            # Multiselect
            # Check for session state to handle standard default if not set
            if 'reorder_selection' not in st.session_state:
                st.session_state['reorder_selection'] = []
                
            selected_pages = st.multiselect(
                "Drag and drop to reorder:", 
                options=page_options,
                default=st.session_state['reorder_selection'],
                key="reorder_multiselect"
            )
            
            if st.button("Process Reorder"):
                if not selected_pages:
                    st.error("Please select at least one page.")
                else:
                    try:
                        # Parse selection specific to "Page X" format
                        indices = [int(p.split(" ")[1]) - 1 for p in selected_pages]
                        
                        with st.spinner("Reordering..."):
                            reordered_pdf = reorder_pdf(pdf_file, indices)
                        
                        st.success("Reordered successfully!")
                        
                        st.download_button(
                            label="Download Reordered PDF",
                            data=reordered_pdf,
                            file_name="reordered_doc.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error processing: {e}")
                    
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
