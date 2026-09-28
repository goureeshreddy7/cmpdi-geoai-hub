"""
analyzer.py — Document analysis using direct Gemini REST API (no SDK)
"""

from typing import Dict
from rag.gemini_client import generate

ANALYSIS_PROMPT = """You are a professional document analyst. Analyze the following document text and produce a structured report.

Respond EXACTLY in this format:

## Executive Summary
Write 3-5 sentences summarizing the entire document.

## Key Points
- Point 1
- Point 2
- Point 3
(List 5-10 most important points as bullets)

## Named Entities
- **People**: list names of people mentioned
- **Organizations**: list company/org names
- **Dates & Numbers**: list important dates and figures
- **Locations**: list places mentioned

## Sentiment & Tone
State the overall sentiment (Positive / Neutral / Negative / Mixed) and explain in 1-2 sentences.

## Document Type
Identify what kind of document this is (e.g., Financial Report, Research Paper, Meeting Minutes, Product Spec, etc.)

## Suggested Questions
List 5 insightful questions a user might want to ask about this document:
1. 
2. 
3. 
4. 
5. 

---
DOCUMENT TEXT:
{document_text}
"""


def analyze_document(pages: list, filename: str, model_name: str = None) -> Dict:
    """
    Generate a structured analysis report for a document.
    """
    full_text = "\n\n".join(p["text"] for p in pages)
    if len(full_text) > 15000:
        full_text = full_text[:15000] + "\n\n[... document truncated for analysis ...]"

    prompt = ANALYSIS_PROMPT.format(document_text=full_text)
    raw_report = generate(prompt, model=model_name, max_tokens=2048)

    return {
        "filename": filename,
        "raw_report": raw_report,
        "page_count": len(pages),
        "char_count": len(full_text),
    }
