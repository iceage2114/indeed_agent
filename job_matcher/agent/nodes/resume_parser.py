"""
parse_resume node — reads the resume file and extracts raw text.
"""

from pathlib import Path

from agent.state import AgentState



def _extract_text(path: Path) -> str:
    ext = path.suffix.lower()

    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    if ext in (".txt", ".md"):
        return path.read_text(encoding="utf-8")

    raise ValueError(f"Unsupported resume format: {ext}")


def parse_resume(state: AgentState) -> dict:
    """LangGraph node. Extracts raw text from the resume file."""
    path = Path(state["resume_path"])

    if not path.exists():
        return {"error": f"Resume file not found: {path}"}

    try:
        resume_text = _extract_text(path)
    except ValueError as exc:
        return {"error": str(exc)}

    print(f"[parse_resume] Extracted {len(resume_text)} characters from {path.name}")

    return {
        "resume_text": resume_text,
        "error":       None,
    }
