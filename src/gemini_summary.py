#!/usr/bin/env python3
"""
Script 2: Summarize PDF(s) using Gemini-2.0 Flash in a single request,
creating .md summaries in data/llm_summaries/<pdf_stem>.md.

Usage:
  python gemini_summary.py --pdf mypaper.pdf
  python gemini_summary.py --pdf all

No logs, no usage token data, no results folder.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

import google.generativeai as genai
from google.generativeai import types

MODEL_NAME = "gemini-2.0-flash"
MAX_OUTPUT_TOKENS = 4096  # Adjust as desired

def load_prompt(prompt_path: Path) -> str:
    """Load the summarization prompt from a text file."""
    if not prompt_path.is_file():
        print(f"Prompt file not found: {prompt_path}")
        sys.exit(1)
    text = prompt_path.read_text(encoding="utf-8").strip()
    if not text:
        print(f"Prompt file is empty: {prompt_path}")
        sys.exit(1)
    return text

def summarize_pdf(pdf_path: Path, prompt: str, output_dir: Path):
    """
    Upload the entire PDF to Gemini-2.0 Flash in one request,
    receive a single text summary. Save the summary to data/llm_summaries/<pdf_stem>.md.
    """
    pdf_stem = pdf_path.stem
    output_file = output_dir / f"{pdf_stem}.md"

    # Create the GenerativeModel object
    model = genai.GenerativeModel(model_name=MODEL_NAME)

    # Upload the PDF
    file_ref = genai.upload_file(str(pdf_path))

    # Generate content
    response = model.generate_content(
        [file_ref, prompt],
        generation_config=types.GenerationConfig(
            temperature=0.0,  # Make it deterministic if you prefer
            max_output_tokens=MAX_OUTPUT_TOKENS
        )
    )

    # Extract text from the response
    summary_text = response.text if (response and response.text) else ""

    # Save the summary
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Summary saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate text summaries for PDFs using Gemini-2.0 Flash")
    parser.add_argument("--pdf", required=True, help="Either a specific PDF filename or 'all'")
    args = parser.parse_args()
    pdf_arg = args.pdf

    # Setup directories
    root_dir = Path(__file__).resolve().parents[1]
    pdfs_dir = root_dir / "data" / "pdfs"
    summaries_dir = root_dir / "data" / "llm_summaries"
    summaries_dir.mkdir(exist_ok=True, parents=True)

    # Load .env for GOOGLE_API_KEY
    load_dotenv(root_dir / "config" / ".env")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set in .env file.")
        sys.exit(1)

    # Configure generative AI with your key
    genai.configure(api_key=api_key)

    # Load summarization prompt
    prompt_path = root_dir / "src" / "prompt.txt"
    prompt_text = load_prompt(prompt_path)

    # If the user provided a single PDF
    if pdf_arg.lower() != "all":
        pdf_path = pdfs_dir / pdf_arg
        if not pdf_path.is_file():
            print(f"PDF not found: {pdf_path}")
            sys.exit(1)
        summarize_pdf(pdf_path, prompt_text, summaries_dir)
        return

    # Otherwise, summarize every PDF in data/pdfs
    for pdf_file in sorted(pdfs_dir.glob("*.pdf")):
        summarize_pdf(pdf_file, prompt_text, summaries_dir)

    print("Done summarizing all PDFs in data/pdfs/.")
    
if __name__ == "__main__":
    main()