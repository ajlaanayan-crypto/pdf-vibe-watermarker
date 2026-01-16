import fitz
from PIL import Image, ImageEnhance
import io
# Streamlit import removed for testability


def process_image(image_file, opacity, rotation):
    """
    Process the uploaded image: apply opacity and rotation.
    Returns: BytesIO object of the processed image.
    """
    image = Image.open(image_file).convert("RGBA")
    
    # 1. Apply Opacity
    if opacity < 1.0:
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        image.putalpha(alpha)
        
    # 2. Apply Rotation
    if rotation != 0:
        # expand=True ensures the corners aren't cut off
        image = image.rotate(-rotation, resample=Image.BICUBIC, expand=True)
        
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr, image.size

def add_watermark(pdf_file, img_bytes, img_size, scale, alignment, x_off, y_off, pages_option, custom_range, is_preview=False):
    """
    Apply watermark to the PDF.
    If is_preview=True, only returns the first page as an image.
    Else, returns the full processed PDF bytes.
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_file.seek(0) # Reset pointer for future use
    
    # Determine pages to process
    if is_preview:
        page_indices = [0]
    elif pages_option == "All Pages":
        page_indices = range(len(doc))
    elif pages_option == "First Page Only":
        page_indices = [0]
    elif pages_option == "Custom Range":
        try:
            parts = [x.strip() for x in custom_range.split(',')]
            indices = set()
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    indices.update(range(start-1, end))
                else:
                    indices.add(int(part) - 1)
            page_indices = sorted(list(indices))
            page_indices = [i for i in page_indices if 0 <= i < len(doc)]
        except:
             # In a library, using print or logging is better than st.error
             print("Invalid page range format. Using All Pages.")
             page_indices = range(len(doc))
    else:
        page_indices = range(len(doc))

    # Watermarking Loop
    for page_index in page_indices:
        page = doc[page_index]
        page_rect = page.rect
        
        # Scale 1.0 = 50% of page width
        wm_width = page_rect.width * scale * 0.5 
        aspect_ratio = img_size[1] / img_size[0]
        wm_height = wm_width * aspect_ratio
        
        # Calculate Base Position
        margin = 20
        
        if alignment == "Center":
            base_x = (page_rect.width - wm_width) / 2
            base_y = (page_rect.height - wm_height) / 2
        elif alignment == "Top-Left":
            base_x = margin
            base_y = margin
        elif alignment == "Top-Right":
            base_x = page_rect.width - wm_width - margin
            base_y = margin
        elif alignment == "Bottom-Left":
            base_x = margin
            base_y = page_rect.height - wm_height - margin
        elif alignment == "Bottom-Right":
            base_x = page_rect.width - wm_width - margin
            base_y = page_rect.height - wm_height - margin
        else:
            base_x = (page_rect.width - wm_width) / 2
            base_y = (page_rect.height - wm_height) / 2

        # Apply offsets
        pos_x = base_x + x_off
        pos_y = base_y + y_off 
        
        # Insert
        rect = fitz.Rect(pos_x, pos_y, pos_x + wm_width, pos_y + wm_height)
        page.insert_image(rect, stream=img_bytes)

    if is_preview:
        pix = doc[0].get_pixmap(dpi=150)
        img_data = pix.tobytes("png")
        doc.close()
        return img_data
    else:
        out_buffer = io.BytesIO()
        doc.save(out_buffer)
        doc.close()
        out_buffer.seek(0)
        return out_buffer
