# ml-document-linker
DocLinker — Intelligent Document Matching System 

Projet de machine learning supervisé visant à rattacher automatiquement des documents administratifs (PDF) à des dossiers existants.

👉 Problème formulé comme une classification binaire supervisée appliquée au ranking (pour chaque document, identifier le bon dossier parmi plusieurs candidats).


## 🚀 Étape 1 : Création du Dataset & Extraction

La phase actuelle du projet se concentre sur la génération de données synthétiques et l'extraction de texte brut.

### 📊 Données Générées
- **Volume** : 200 documents PDF synthétiques.
- **Style** : Documents administratifs type DT-DICT.
- **Qualité** : 10 à 20 % des documents contiennent volontairement du "bruit" (erreurs d'extraction, texte dégradé) pour tester la robustesse des futurs modèles.
- **Cibles** : 80 dossiers de destination possibles.

### 🛠️ Pipeline de Traitement
1. **Génération** : Création des PDF, de la base des dossiers candidats et de la vérité terrain.
`cases.csv` : Base des dossiers candidats (80 lignes).
    - Équivalent de la base de dossiers existants en entreprise
    - Chaque ligne représente un dossier candidat
    - Ce sont les cibles possibles pour le rattachement
    - Chaque PDF devra être rattaché à un et un seul de ces dossiers

`ground_truth.csv` : Fichier de vérité terrain (labels).
    - Chaque ligne indique le rattachement correct entre un PDF et un dossier
    - Sert à entraîner et évaluer les modèles supervisés

Reproductibilité 
- Données générées de manière déterministe
- Seed utilisé : 42

2. **Extraction** : Utilisation de `pdfplumber` pour transformer les PDF en texte brut.
3. **Structuration** : Export vers un dataset consolidé `pdf_texts.csv`.

## 📁 Structure du Projet

```text
ML-DOCUMENT-LINKER/
├── data/
│   └── synthetic/
│       ├── pdfs/               # (Local uniquement) 200 fichiers sources
│       ├── ground_truth.csv    # Labels : correspondance PDF <-> Dossier
│       └── pdf_texts.csv       # Dataset extrait (pdf_id, name, text, len)
├── notebooks/
│   └── 01_extract_pdf_texts.ipynb
├── src/
│   └── data/
│       └── extract_pdf_texts.py # Script d'extraction automatisé
├── .gitignore                  # Exclusion du venv et des PDF lourds
└── README.md

____

Commentaires dans les CSV 
Les fichiers CSV peuvent contenir des commentaires en tête de fichier, préfixés par #.


Comment="#"
Plus tard pour que pandas le lise mais ignore les commentaires : 
    pd.read_csv("cases.csv", comment="#")
