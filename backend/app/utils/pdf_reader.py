# ============================================
# NEXORA AI - PDF Reader Utility
# ============================================
# PDF ফাইল থেকে text extract করে।
# PyPDF2 ব্যবহার করে lightweight processing।

import PyPDF2
import os
from typing import List, Dict
from app.core.logger import logger


def extract_text_from_pdf(file_path: str) -> Dict:
    """
    PDF ফাইল থেকে সব text বের করে।
    প্রতিটি page আলাদাভাবে রাখা হয়।
    
    Returns:
        {
            "total_pages": int,
            "pages": [{"page_num": int, "text": str}],
            "full_text": str,
            "word_count": int
        }
    """
    result = {
        "total_pages": 0,
        "pages": [],
        "full_text": "",
        "word_count": 0
    }

    if not os.path.exists(file_path):
        logger.error(f"PDF file not found: {file_path}")
        return result

    try:
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            result["total_pages"] = len(reader.pages)

            full_text_parts = []

            for page_num, page in enumerate(reader.pages):
                # Page থেকে text extract
                page_text = page.extract_text()

                if page_text:
                    # Text clean করা
                    cleaned_text = clean_extracted_text(page_text)

                    result["pages"].append({
                        "page_num": page_num + 1,
                        "text": cleaned_text
                    })

                    full_text_parts.append(cleaned_text)

            # সব page এর text একসাথে জোড়া
            result["full_text"] = "\n\n".join(full_text_parts)
            result["word_count"] = len(result["full_text"].split())

            logger.info(
                f"✅ PDF extracted: {result['total_pages']} pages, "
                f"{result['word_count']} words"
            )

    except Exception as e:
        logger.error(f"❌ PDF extraction error: {e}")

    return result


def clean_extracted_text(text: str) -> str:
    """
    PDF থেকে বের করা text clean করে।
    Extra spaces, newlines, special characters সরায়।
    """
    import re

    # Multiple spaces → single space
    text = re.sub(r' +', ' ', text)

    # Multiple newlines → double newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Null characters সরানো
    text = text.replace('\x00', '')

    # Line শুরু/শেষের spaces সরানো
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)

    return text.strip()


def get_pdf_metadata(file_path: str) -> Dict:
    """
    PDF এর metadata বের করে (author, title, etc.)
    """
    metadata = {}

    try:
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)

            if reader.metadata:
                metadata = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "subject": reader.metadata.get("/Subject", ""),
                    "pages": len(reader.pages)
                }
    except Exception as e:
        logger.error(f"Metadata extraction error: {e}")

    return metadata
