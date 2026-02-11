# src/generate_synthetic_pdfs.py
from __future__ import annotations

import random
import string
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1] # Permet d'avoir la racine du projet, parents[1] remonte de 2 niveau sur le chemin absolu du fichier
OUT_DIR = ROOT / "data" / "synthetic" #Dossier où on stocke tout le dataset synthétique
PDF_DIR = OUT_DIR / "pdfs" # Sous-dossier où on met les PDFs
PDF_DIR.mkdir(parents=True, exist_ok=True) #Crée le dossier si besoin (sans erreur s'il existe déjà)

# Prend 
def rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def format_date(dt: datetime) -> str:
    fmts = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%y"]
    return dt.strftime(random.choice(fmts))


def fuzz_text(s: str, p_typo: float = 0.12) -> str:
    """Injecte quelques perturbations réalistes."""
    if not s:
        return s
    chars = list(s)
    for i in range(len(chars)):
        if random.random() < p_typo and chars[i].isalpha():
            # petite altération: suppression ou remplacement
            r = random.random()
            if r < 0.33:
                chars[i] = ""  # suppression
            elif r < 0.66:
                chars[i] = chars[i].upper() if chars[i].islower() else chars[i].lower()
            else:
                chars[i] = random.choice(string.ascii_letters)
    out = "".join(chars)
    # espaces multiples
    if random.random() < 0.2:
        out = out.replace(" ", "  ")
    return out.strip()


TEMPLATES = [
    "DT/DICT\nRéférence dossier : {ref}\nCommune : {commune}\nCode postal : {cp}\nDate : {date}\nDemandeur : {demandeur}\nEntreprise : {entreprise}\nAdresse : {adresse}\n\n{blabla}",
    "Déclaration de Travaux\nDossier n° {ref}\nVille: {commune} ({cp})\nDemandeur: {demandeur}\nSociété: {entreprise}\nFait le {date}\nLieu: {adresse}\n\n{blabla}",
    "FORMULAIRE ADMINISTRATIF\n{blabla}\n---\nREF={ref}\nCOMMUNE={commune}\nCP={cp}\nDATE_DEMANDE={date}\nDEMANDEUR={demandeur}\nENTREPRISE={entreprise}\nADRESSE={adresse}\n---\n{blabla}",
    "DT-DICT\n{blabla}\nRéf.: {ref}\nAdresse chantier: {adresse}\nCommune: {commune}\nDate de la demande: {date}\nDemandeur: {demandeur}\nEntreprise exécutante: {entreprise}\n{blabla}",
]

BLABLA_LINES = [
    "Conformément aux dispositions en vigueur, merci de traiter la demande dans les délais réglementaires.",
    "Le présent document comporte des informations administratives et techniques relatives à l'intervention.",
    "Veuillez vérifier la présence éventuelle de réseaux sensibles sur la zone concernée.",
    "Les coordonnées sont fournies à titre indicatif et peuvent nécessiter une validation.",
    "Document généré automatiquement pour test de traitement documentaire.",
]


def make_blabla(n_lines: int) -> str:
    return "\n".join(random.choice(BLABLA_LINES) for _ in range(n_lines))


def build_cases(n_cases: int = 80) -> pd.DataFrame:
    communes = [
        ("Nanterre", "92000"),
        ("Paris", "75012"),
        ("Montreuil", "93100"),
        ("Versailles", "78000"),
        ("Boulogne-Billancourt", "92100"),
        ("Saint-Denis", "93200"),
        ("Ivry-sur-Seine", "94200"),
    ]
    entreprises = ["XYZ Réseaux", "ABC Travaux", "InfraSud", "GeoBat", "NordCable", "RéseauPro"]
    demandeurs = ["Mairie", "Société Durand", "SAS Martin", "Entreprise Leroy", "Agence Voirie"]

    rows = []
    start = datetime(2023, 1, 1)
    end = datetime(2026, 2, 1)

    for i in range(1, n_cases + 1):
        commune, cp = random.choice(communes)
        ref = f"DT-{random.randint(2023, 2026)}-{i:05d}"
        dt = rand_date(start, end)
        demandeur = random.choice(demandeurs)
        entreprise = random.choice(entreprises)
        adresse = f"{random.randint(1, 200)} rue {random.choice(['des Lilas','Victor Hugo','de la Paix','Jean Jaurès','Pasteur'])}"
        rows.append({
            "case_id": f"C{i:05d}",
            "ref": ref,
            "date": dt.strftime("%Y-%m-%d"),
            "commune": commune,
            "cp": cp,
            "demandeur": demandeur,
            "entreprise": entreprise,
            "adresse": adresse
        })
    return pd.DataFrame(rows)


def render_pdf(text: str, out_path: Path) -> None:
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    x, y = 40, height - 50
    for line in text.split("\n"):
        c.drawString(x, y, line[:110])  # coupe pour éviter débordement
        y -= 14
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()


def generate_pdfs(n_pdfs: int = 200) -> None:
    cases = build_cases(n_cases=80)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases.to_csv(OUT_DIR / "cases.csv", index=False)

    gt_rows = []

    for i in range(1, n_pdfs + 1):
        pdf_id = f"P{i:05d}"
        # rattachement vrai = un case choisi
        case = cases.sample(1, random_state=random.randint(0, 10_000)).iloc[0]

        # champs parfois manquants (simule réalité)
        missing = set()
        if random.random() < 0.10: missing.add("adresse")
        if random.random() < 0.08: missing.add("demandeur")
        if random.random() < 0.06: missing.add("entreprise")

        data = {
            "ref": fuzz_text(case["ref"], p_typo=0.05 if random.random() < 0.7 else 0.15),
            "commune": fuzz_text(case["commune"], p_typo=0.05),
            "cp": case["cp"],
            "date": format_date(datetime.strptime(case["date"], "%Y-%m-%d")),
            "demandeur": "" if "demandeur" in missing else fuzz_text(case["demandeur"], p_typo=0.08),
            "entreprise": "" if "entreprise" in missing else fuzz_text(case["entreprise"], p_typo=0.08),
            "adresse": "" if "adresse" in missing else fuzz_text(case["adresse"], p_typo=0.10),
            "blabla": make_blabla(n_lines=random.randint(6, 14)),
        }

        template = random.choice(TEMPLATES)
        doc_text = template.format(**data)

        out_pdf = PDF_DIR / f"{pdf_id}.pdf"
        render_pdf(doc_text, out_pdf)

        gt_rows.append({"pdf_id": pdf_id, "case_id": case["case_id"]})

    pd.DataFrame(gt_rows).to_csv(OUT_DIR / "ground_truth.csv", index=False)
    print(f"✅ Generated {n_pdfs} PDFs in {PDF_DIR}")
    print(f"✅ cases.csv and ground_truth.csv saved in {OUT_DIR}")


if __name__ == "__main__":
    generate_pdfs(n_pdfs=200)
