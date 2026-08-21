"""
Unisce più immagini in un singolo PDF (PyMuPDF/fitz — img2pdf NON installato).

Uso:
  python3 photos_to_pdf.py <out.pdf> <img1> [<img2> ...]

Ogni immagine diventa una pagina con le stesse proporzioni.
"""
import sys
from pathlib import Path

import fitz  # PyMuPDF


def photos_to_pdf(image_paths: list[str], out_pdf: str) -> None:
    doc = fitz.open()
    for img in image_paths:
        pix = fitz.Pixmap(str(img))
        # Converti CMYK/altri colorspaces in RGB
        if pix.colorspace and pix.colorspace.n > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        page = doc.new_page(width=pix.width, height=pix.height)
        page.insert_image(page.rect, pixmap=pix)
    doc.save(out_pdf, deflate=True)
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python photos_to_pdf.py <out.pdf> <img1> [<img2> ...]", file=sys.stderr)
        sys.exit(1)
    out = sys.argv[1]
    if Path(out).exists():
        print(f"ERRORE: {out} esiste già", file=sys.stderr)
        sys.exit(1)
    photos_to_pdf(sys.argv[2:], out)
    print(f"OK: {out} ({len(sys.argv) - 2} pagine)")
