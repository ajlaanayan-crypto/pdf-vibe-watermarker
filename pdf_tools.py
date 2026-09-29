import fitz  # PyMuPDF
import io
from PIL import Image

def merge_pdfs(file_list):
    """
    Merges multiple PDFs and Images into a single PDF.
    file_list: List of UploadedFile objects (or similar objects with read() and name attributes)
    Returns: BytesIO object of the merged PDF.
    """
    merged_doc = fitz.open()

    for file in file_list:
        file.seek(0)
        file_name = file.name.lower()

        if file_name.endswith(('.pdf')):
            # Append PDF
            try:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                merged_doc.insert_pdf(doc)
                doc.close()
            except Exception as e:
                print(f"Error merging PDF {file.name}: {e}")
        
        elif file_name.endswith(('.png', '.jpg', '.jpeg')):
            # Convert Image to PDF page
            try:
                img = Image.open(file)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="PDF")
                img_byte_arr.seek(0)
                
                img_doc = fitz.open(stream=img_byte_arr.read(), filetype="pdf")
                merged_doc.insert_pdf(img_doc)
                img_doc.close()
            except Exception as e:
                print(f"Error merging Image {file.name}: {e}")

    out_buffer = io.BytesIO()
    merged_doc.save(out_buffer)
    merged_doc.close()
    out_buffer.seek(0)
    return out_buffer

def reorder_pdf(pdf_file, new_order_list):
    """
    Reorders pages of a PDF based on a list of indices.
    pdf_file: UploadedFile or BytesIO
    new_order_list: List of integers representing 0-indexed page numbers.
    Returns: BytesIO object of the new PDF.
    """
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    
    # Create a new empty PDF
    new_doc = fitz.open()
    
    # Validate indices
    valid_indices = [i for i in new_order_list if 0 <= i < len(doc)]
    
    if not valid_indices:
        # Fallback if no valid pages selected
        new_doc.insert_pdf(doc)
    else:
        new_doc.insert_pdf(doc, from_page=-1, to_page=-1, start_at=-1) # Dummy call, actually using select is better or insert_pdf with selection
        # Actually PyMuPDF install_pdf allows selecting pages.
        # But easier way: 
        new_doc.close()
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=-1, to_page=-1) # Reset
        # Wait, the best way to reorder in PyMuPDF is doc.select(seq)
        doc.select(valid_indices) 
        # doc.select modifies the doc in-place.
        
        out_buffer = io.BytesIO()
        doc.save(out_buffer)
        doc.close()
        out_buffer.seek(0)
        return out_buffer

    # If we fell through (shouldn't happen with the select approach)
    out_buffer = io.BytesIO()
    doc.save(out_buffer)
    doc.close()
    out_buffer.seek(0)
    return out_buffer

def get_pdf_previews(pdf_file, dpi=72):
    """
    Generates previews for all pages in a PDF.
    Returns: List of PIL Images.
    """
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    
    previews = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        previews.append(img)
    
    doc.close()
    return previews
