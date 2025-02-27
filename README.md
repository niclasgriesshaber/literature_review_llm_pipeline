# 📚 LLM Patent Literature Review 🔍

This repository contains a toolkit for scraping patent PDFs and generating AI-powered summaries using Google's Gemini model. The summaries can be viewed and organized in Obsidian for easy navigation and research.

## 🗂️ Project Structure

```
.
├── config/                    # Configuration files
│   ├── .env                   # Environment variables (API keys)
│   └── environment.yml        # Conda environment specification
│
├── data/                      # Data storage
│   ├── pdfs/                  # Downloaded patent PDFs
│   ├── llm_summaries/         # Generated LLM summaries
│   └── deepresearch_review.xlsx # Input data with patent links
│
├── src/                       # Source code
│   ├── scrape_pdfs.py         # Script to download PDFs from links
│   ├── gemini_summary.py      # Single file summary generator
│   ├── gemini_summary_async.py # Asynchronous summary generator
│   ├── concatenate_summaries.py # Tool to combine all summaries
│   └── prompt.txt             # Customizable prompt for the LLM
│
└── README.md                  # This file
```

## 🛠️ Setup Instructions

### 1. 📥 Install Conda

If you don't have Conda installed yet:

- Download and install Miniconda from: https://docs.conda.io/en/latest/miniconda.html
- Or Anaconda from: https://www.anaconda.com/products/distribution

### 2. 🐍 Create and Activate the Conda Environment

```bash
# Create the environment using the provided environment.yml
conda env create -f config/environment.yml

# Activate the environment
conda activate llm_patent_review
```

### 3. 🔑 Configure API Keys

Create or edit the `.env` file in the `config` directory with your Google API key:

```
GOOGLE_API_KEY=your_api_key_here
```

## 🚀 Usage

### 1. 📋 Scrape Patent PDFs

The starting point is the `deepresearch_review.xlsx` file containing patent links.

```bash
python src/scrape_pdfs.py
```

This will download the PDFs from the links in the Excel file and save them to the `data/pdfs/` directory.

### 2. ✏️ Customize the Prompt

Edit the `src/prompt.txt` file to customize what information the LLM should extract or focus on when generating summaries. Tailor this to your specific research needs.

### 3. 🤖 Generate Summaries

Run the asynchronous summary generator to process all PDFs:

```bash
python src/gemini_summary_async.py
```

This will:
- Process each PDF in the `data/pdfs/` directory
- Apply your customized prompt to each document
- Generate summaries in markdown format
- Save them to the `data/llm_summaries/` directory

For processing a single file, you can alternatively use:

```bash
python src/gemini_summary.py path/to/specific/pdf
```

### 4. 👁️ View Summaries in Obsidian

1. Download and install Obsidian: https://obsidian.md/download
2. Open Obsidian
3. Choose "Open folder as vault"
4. Select the `data/llm_summaries/` directory from this project

Now you can browse, search, and link your patent summaries in Obsidian's powerful knowledge management interface.

### 5. 🔄 Generate Combined Summary and Analyze Research Gaps

As the final step, combine all summaries into a single file:

```bash
python src/concatenate_summaries.py
```

This will create `data/concatenated_summaries.txt` with all summaries combined.

Then:
1. 🌐 Open Google AI Studio (https://ai.google.dev/)
2. ✨ Create a new prompt with the gemini-2.0-flash model
3. 📝 Copy and paste the contents of `data/concatenated_summaries.txt` into the prompt
4. 💡 Ask about gaps in the literature, for example:
   - "Based on these patent summaries, what are the major gaps in the current technology?"
   - "What research areas are underexplored according to these patents?"
   - "What opportunities for innovation can you identify from analyzing these patents?"

## 📦 Dependencies

Key dependencies include:
- Python 3.8+ 🐍
- Google Gemini API 🤖
- PyPDF2 📄
- pandas 🐼
- aiohttp 🌐
- tqdm 📊

All dependencies are specified in the `config/environment.yml` file. 