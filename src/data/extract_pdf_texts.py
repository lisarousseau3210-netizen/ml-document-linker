import pandas as pd
import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extrait le texte de toutes les pages d'un PDF."""
    texts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                texts.append(page_text)
    except Exception as e:
        print(f"❌ Erreur sur le fichier {pdf_path.name}: {e}")
        return ""
    return "\n".join(texts).strip()

def main():
    # --- CONFIGURATION DES CHEMINS ---
    # __file__ est le chemin du script actuel (src/data/extract_pdf_texts.py)
    # .parents[2] remonte de 2 niveaux pour arriver à la racine du projet
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    
    PDF_DIR = PROJECT_ROOT / "data" / "synthetic" / "pdfs"
    OUT_CSV = PROJECT_ROOT / "data" / "synthetic" / "pdf_texts.csv"

    print(f"🔍 Recherche des PDFs dans : {PDF_DIR}")

    # --- VERIFICATION ---
    if not PDF_DIR.exists():
        print(f"🛑 Erreur : Le dossier {PDF_DIR} n'existe pas.")
        return

    pdf_paths = sorted(PDF_DIR.glob("*.pdf"))
    print(f"📂 {len(pdf_paths)} PDFs trouvés. Début de l'extraction...")

    # --- EXTRACTION ---
    rows = []
    for p in pdf_paths:
        text = extract_text_from_pdf(p)
        rows.append({
            "pdf_id": p.stem,
            "file_name": p.name,
            "text": text,
            "text_len": len(text),
        })

    # --- SAUVEGARDE ---
    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    
    print("-" * 30)
    print(f"✅ Terminé ! {len(df)} fichiers traités.")
    print(f"💾 Résultat sauvegardé ici : {OUT_CSV}")
    print("-" * 30)

if __name__ == "__main__":
    main()