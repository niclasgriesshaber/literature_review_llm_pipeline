#!/usr/bin/env python3
"""
Script 2 (Parallel): Summarize PDF(s) using Gemini-2.0 Flash in parallel,
creating .md summaries in data/llm_summaries/<pdf_stem>.md.

Usage:
  python gemini_summary_parallel.py --pdf mypaper.pdf
  python gemini_summary_parallel.py --pdf all

- No logs beyond minimal prints.
- No usage token data, no extra results folder.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

import google.generativeai as genai
from google.generativeai import types

MODEL_NAME = "gemini-2.0-flash"
MAX_OUTPUT_TOKENS = 4096  # Adjust as desired

# Parallel settings
MAX_WORKERS = 500            # Adjust concurrency as needed
RETRY_LIMIT_SECONDS = 120  # 2 minutes total to keep retrying 429
BACKOFF_SLEEP_SECONDS = 10  # Sleep time on 429 before retrying

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
    Upload the entire PDF to Gemini-2.0 Flash in one request.
    Receive a single text summary. Save to data/llm_summaries/<pdf_stem>.md
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

    return output_file  # Return the path of the newly created .md

def summarize_pdf_with_retry(pdf_path: Path, prompt: str, output_dir: Path):
    """
    Wraps summarize_pdf with a simple retry loop for 429 'Resource Exhausted' errors.
    """
    start_time = time.time()
    attempt = 1
    while True:
        try:
            output_file = summarize_pdf(pdf_path, prompt, output_dir)
            return output_file
        except Exception as e:
            msg = str(e)
            # Check for 429 or resource-exhausted signals
            if ("429" in msg or "RESOURCE_EXHAUSTED" in msg) and \
               (time.time() - start_time < RETRY_LIMIT_SECONDS):
                attempt += 1
                print(f"[{pdf_path.name}] Got 429/Resource Exhausted. Backoff #{attempt}...")
                time.sleep(BACKOFF_SLEEP_SECONDS)
            else:
                # Not a 429 or we ran out of time
                raise

def main():
    parser = argparse.ArgumentParser(description="Generate text summaries for PDFs using Gemini-2.0 Flash (Parallel).")
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

    # If the user provided a single PDF, do a single summary (no parallel needed)
    if pdf_arg.lower() != "all":
        pdf_path = pdfs_dir / pdf_arg
        if not pdf_path.is_file():
            print(f"PDF not found: {pdf_path}")
            sys.exit(1)
        try:
            output_file = summarize_pdf_with_retry(pdf_path, prompt_text, summaries_dir)
            print(f"Summary saved to: {output_file}")
        except Exception as e:
            print(f"Error summarizing {pdf_arg}: {e}")
        return

    # Otherwise, summarize every PDF in data/pdfs in parallel
    pdf_files = sorted(pdfs_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {pdfs_dir}")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDFs. Summarizing in parallel (max_workers={MAX_WORKERS})...")
    futures = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for pdf_path in pdf_files:
            fut = executor.submit(summarize_pdf_with_retry, pdf_path, prompt_text, summaries_dir)
            futures[fut] = pdf_path

        for fut in as_completed(futures):
            pdf_path = futures[fut]
            try:
                output_file = fut.result()
                print(f"✔ {pdf_path.name} => Summary saved to: {output_file}")
            except Exception as e:
                print(f"✖ {pdf_path.name} => Error: {e}")

    print("Done summarizing all PDFs in data/pdfs/.")

if __name__ == "__main__":
    main()