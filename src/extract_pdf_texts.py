from pathlib import Path
import pandas as pd
import pdfplumber

# Chemins
PROJECT_ROOT = Path.cwd().parent  # si ton notebook est dans /notebooks
PDF_DIR = PROJECT_ROOT / "data" / "synthetic" / "pdfs"
OUT_CSV = PROJECT_ROOT / "data" / "synthetic" / "pdf_texts.csv"

PDF_DIR, PDF_DIR.exists(), OUT_CSV