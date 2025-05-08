import fitz
from PIL import Image
import os

def generate_thumbnail(pdf_path, output_dir="thumbnails", size=(200, 200)):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.thumbnail(size)
    thumbnail_path = os.path.join(output_dir, f"thumb_{os.path.basename(pdf_path)}.png")
    img.save(thumbnail_path)
    return thumbnail_path