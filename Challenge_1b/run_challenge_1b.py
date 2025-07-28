import os
import json
import fitz  # PyMuPDF
from datetime import datetime

base_path = "."
collections = [f for f in os.listdir(base_path) if f.startswith("Collection")]

# keywords = ["trip", "college", "group", "friends", "cities", "hotels", "restaurants",
#             "culture", "nightlife", "things to do", "tips", "beaches", "adventure"]

# def score_text(text):
#     return sum(text.lower().count(k) for k in keywords)

# Better keyword categories with weights
keyword_weights = {
    "things to do": 5,
    "activities": 4,
    "nightlife": 4,
    "beaches": 4,
    "adventure": 4,
    "cuisine": 4,
    "restaurants": 3,
    "food": 3,
    "culture": 2,
    "cities": 2,
    "hotels": 2,
    "tips": 2,
    "packing": 2,
    "travel": 2,
    "trip": 3,
    "group": 2,
    "friends": 2,
    "college": 2
}

def score_text(text):
    text_lower = text.lower()
    return sum(text_lower.count(k) * w for k, w in keyword_weights.items())


for collection in collections:
    folder_path = os.path.join(base_path, collection)
    input_json = os.path.join(folder_path, "challenge1b_input.json")
    pdf_dir = os.path.join(folder_path, "pdfs")
    output_json = os.path.join(folder_path, "generated_output.json")

    with open(input_json, "r") as f:
        data = json.load(f)

    persona = data["persona"]["role"]
    job = data["job_to_be_done"]["task"]
    pdfs = data["documents"]

    extracted_sections = []
    subsection_analysis = []

    for doc in pdfs:
        filename = doc["filename"]
        pdf_path = os.path.join(pdf_dir, filename)
        doc_pdf = fitz.open(pdf_path)

        for page_num, page in enumerate(doc_pdf, start=1):
            text = page.get_text()
            score = score_text(text)
            if score >= 3:
                title = text.split("\n")[0][:100]
                extracted_sections.append({
                    "document": filename,
                    "section_title": title,
                    "importance_rank": len(extracted_sections) + 1,
                    "page_number": page_num
                })
                subsection_analysis.append({
                    "document": filename,
                    "refined_text": text[:1000],
                    "page_number": page_num
                })
            if len(extracted_sections) >= 5:
                break

    final_output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in pdfs],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)

    print(f"✅ Done: {collection} → {output_json}")
