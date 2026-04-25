# 🇮🇳 Sarkar Sahayak — Government Scheme Assistant MVP

An AI-assisted Streamlit web app to help Indian citizens discover government schemes, check eligibility, and fill application forms in English or Hindi.

---

## 📁 File Structure

```
sarkar-sahayak/
├── app.py              ← Main Streamlit application
├── schemes.json        ← Dataset of government schemes
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## ⚙️ Setup & Run

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 🔍 Features

| Feature | Description |
|---|---|
| **Search** | Type queries like "PM Kisan", "ration card", "health insurance" |
| **Scheme Info** | Name, description, eligibility, required documents, ministry, benefit |
| **Language Toggle** | Switch between English and Hindi in the sidebar |
| **Application Form** | Fields: Name, DOB, Address, Aadhaar, Income, Mobile, State |
| **Field Guidance** | Yellow hint boxes beside each field explain how to fill it |
| **Validation** | Aadhaar (12 digits), Mobile (10 digits), required field checks |

---

## 📋 Schemes in Dataset

1. PM Kisan Samman Nidhi
2. Ration Card (PDS)
3. Ayushman Bharat (PM-JAY)
4. Pradhan Mantri Ujjwala Yojana
5. Pradhan Mantri Jan Dhan Yojana
6. Pradhan Mantri Mudra Yojana

---

## 🛠️ Adding More Schemes

Edit `schemes.json` and add a new entry following this structure:

```json
{
  "id": "unique_id",
  "name": "Scheme Name",
  "keywords": ["keyword1", "keyword2"],
  "description": "What the scheme does.",
  "eligibility": ["Criterion 1", "Criterion 2"],
  "documents": ["Document 1", "Document 2"],
  "ministry": "Ministry Name",
  "benefit": "Key benefit description"
}
```

---

## 📝 Notes

- Translation is built-in via a Python dictionary (no external API needed)
- The app is intentionally offline-friendly for rural/low-connectivity demos
- Data is illustrative and meant for hackathon demonstration only







# ── States ───────────────────────────────────────────────────────────────────
STATES = [
    "Delhi",
    "Uttar Pradesh",
    "Haryana",
    "Punjab",
    "Rajasthan",
    "Maharashtra",
    "Karnataka",
    "Tamil Nadu",
    "West Bengal",
    "Gujarat"