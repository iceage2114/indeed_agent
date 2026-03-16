# Cover Letter Skill

Rewrites the first paragraph of a cover letter template to be precisely tailored to a specific job description, using your resume and persistent personal writing preferences.

---

## Files

| File                        | Purpose                                                                 |
|-----------------------------|-------------------------------------------------------------------------|
| `run.py`                    | Entry point — fills the prompt and calls the LLM API                   |
| `prompt.md`                 | LLM prompt template with `{{placeholders}}`                             |
| `personal_notes.md`         | Your persistent tone and style preferences (edit once, always applied)  |
| `SKILL.md`                  | Full skill specification and nanobot integration reference              |
| `documents/cover_letter.md` | Your cover letter template                                              |
| `documents/resume.md`       | Your resume                                                             |
| `documents/job_description.md` | The job posting you're applying to                                   |

---

## Setup

**1. Create and activate a virtual environment**

From the `cover_letter_skill/` directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**2. Install dependencies**

```powershell
pip install openai python-dotenv
```

**3. Configure your API key**

Make sure your `.env` file in the project root contains:

```
GITHUB_TOKEN=your_token_here
```

The script uses the GitHub Models endpoint (`https://models.inference.ai.azure.com`).

---

## Quickstart

**1. Set your writing preferences (once)**

Open `personal_notes.md` and fill in how you want your cover letters to sound — tone, things to avoid, opening style, etc. This file is loaded automatically on every run.

**2. Run**

From the project root — no arguments needed if your files are in `documents/`:

```powershell
python cover_letter_skill/run.py
```

Or point at custom paths:

```powershell
python cover_letter_skill/run.py `
  --cover-letter path/to/cover_letter.md `
  --resume       path/to/resume.md `
  --job-description path/to/job_description.md
```

All three arguments accept any plain text or markdown file.

**3. Use the output**

The script prints the tailored first paragraph. Replace the first paragraph of your cover letter template with it — the rest of the letter stays the same.

---

## How It Works

1. Loads `personal_notes.md` as hard style constraints.
2. Reads the job description and identifies the top requirements the employer cares about.
3. Scans the resume for the strongest matching qualification.
4. Rewrites the first paragraph to open with a specific hook, reference the role and company, and highlight the most relevant experience — all within your preferred tone and voice.
5. Returns only the new paragraph, nothing else.

---

## Customization

- **Change the model** — set `LLM_MODEL` in your `.env` (default: `gpt-4o`).
- **Change prompt behavior** — edit `prompt.md` directly.
- **Update preferences** — edit `personal_notes.md` at any time.
