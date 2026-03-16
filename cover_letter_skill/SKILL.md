# Skill: Cover Letter First Paragraph Tailor

## Description
Given a cover letter template, a resume, and a job description, this skill rewrites only the **first paragraph** of the cover letter to be highly relevant to the specific role. The rest of the cover letter is left unchanged.

## Persistent Memory

| File                                          | Description                                                                 |
|-----------------------------------------------|-----------------------------------------------------------------------------|
| `cover_letter_skill/personal_notes.md`        | Your tone, voice, and style preferences. Edit once, always applied.         |

Edit `personal_notes.md` to set your preferences. The nanobot loads it automatically on every run — you do not pass it as an input.

## Per-Run Inputs

| Variable              | Description                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------------|
| `{{cover_letter}}`    | The full cover letter template (plain text or markdown)                                          |
| `{{resume}}`          | The applicant's resume (plain text or markdown)                                                  |
| `{{job_description}}` | The full job description for the target role                                                     |

## Output
A single tailored first paragraph (plain text, ready to drop into the cover letter).

## Usage in Nanobot
Point your nanobot at `prompt.md`. Bind `personal_notes` to the persistent file (loaded once at startup) and the remaining three as per-run inputs.

```yaml
skill: cover_letter_first_paragraph
prompt_file: cover_letter_skill/prompt.md
memory:
  personal_notes: cover_letter_skill/personal_notes.md
inputs:
  cover_letter: "<contents of cover letter template>"
  resume: "<contents of resume>"
  job_description: "<contents of job description>"
```

## What the Skill Does
1. Reads your personal notes and locks in your tone, voice, and style preferences as hard constraints.
2. Reads the job description and identifies the top 3–5 requirements/themes the employer cares about most.
3. Scans the resume for the most relevant matching experience, skills, and achievements.
4. Rewrites the first paragraph of the cover letter to:
   - Open with a strong, specific hook tied to the role or company.
   - Reference the exact job title and company name (if present in the job description).
   - Highlight the single most compelling qualification from the resume that maps to the role.
   - Signal genuine, informed interest in this position.
4. Returns **only** the new first paragraph — no explanations, no extra text.

## Prompt File
See `prompt.md` for the full LLM prompt template.
