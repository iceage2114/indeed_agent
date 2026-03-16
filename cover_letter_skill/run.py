"""
cover_letter_skill/run.py

Tailors the first paragraph of a cover letter to a specific job description.

Usage (default paths):
    python run.py

Usage (custom paths):
    python run.py --cover-letter <path> --resume <path> --job-description <path>

Drops your documents in cover_letter_skill/documents/ and run with no arguments.
personal_notes.md is loaded automatically from this directory.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SKILL_DIR   = Path(__file__).parent
ROOT_DIR    = SKILL_DIR.parent
DOCS_DIR    = SKILL_DIR / "documents"
PROMPT_FILE = SKILL_DIR / "prompt.md"
NOTES_FILE  = SKILL_DIR / "personal_notes.md"

# Load .env from the project root
load_dotenv(ROOT_DIR / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    sys.exit("Error: set GITHUB_TOKEN in your .env file.")

api_key  = GITHUB_TOKEN
base_url = "https://models.inference.ai.azure.com"
model    = os.getenv("LLM_MODEL", "gpt-4o")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        sys.exit(f"Error: file not found — {path}")


def fill_prompt(template: str, **kwargs) -> str:
    for key, value in kwargs.items():
        template = template.replace("{{" + key + "}}", value)
    return template


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Tailor cover letter first paragraph.")
    parser.add_argument("--cover-letter",    default=DOCS_DIR / "cover_letter.md",    type=Path, help="Path to cover letter template (default: documents/cover_letter.md)")
    parser.add_argument("--resume",          default=DOCS_DIR / "resume.md",          type=Path, help="Path to resume file (default: documents/resume.md)")
    parser.add_argument("--job-description", default=DOCS_DIR / "job_description.md", type=Path, help="Path to job description file (default: documents/job_description.md)")
    args = parser.parse_args()

    prompt_template = read(PROMPT_FILE)
    personal_notes  = read(NOTES_FILE)
    cover_letter    = read(args.cover_letter)
    resume          = read(args.resume)
    job_description = read(args.job_description)

    prompt = fill_prompt(
        prompt_template,
        personal_notes=personal_notes,
        cover_letter=cover_letter,
        resume=resume,
        job_description=job_description,
    )

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    paragraph = response.choices[0].message.content.strip()
    print("\n--- Tailored First Paragraph ---\n")
    print(paragraph)
    print()


if __name__ == "__main__":
    main()
