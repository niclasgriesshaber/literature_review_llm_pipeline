import os
import glob

def concatenate_markdown_files():
    # Determine absolute path to the folder containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct path to ../data/llm_summaries (one level up from src)
    md_folder = os.path.join(script_dir, "..", "data", "llm_summaries")
    
    # Pattern to find all .md files in the specified folder
    md_files = glob.glob(os.path.join(md_folder, "*.md"))
    md_files.sort()  # Sort file list for a predictable order (optional)

    if not md_files:
        print(f"No .md files found in {md_folder}")
        return

    output_path = os.path.join(script_dir, "..", "data", "concatenated_summaries.txt")
    print(f"Writing all summaries to: {output_path}")

    with open(output_path, "w", encoding="utf-8") as outfile:
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as infile:
                content = infile.read()
            
            outfile.write(content)
            outfile.write("\n\n")  # Add blank lines between files

    print("Done! All .md files have been concatenated.")

if __name__ == "__main__":
    concatenate_markdown_files()