from typing import TypedDict, Optional


class JobCandidate(TypedDict):
    id: str
    title: str
    company: str
    location: str
    description: str            # short description pulled from DB
    url: str
    date_posted: str
    field: str
    easy_apply: bool
    similarity_score: Optional[float]   # cosine similarity vs resume embedding


class AgentState(TypedDict):
    resume_path: str
    resume_text: str                    # raw text extracted from resume file
    resume_embedding: list              # embedding vector of full resume text
    all_jobs: list                      # list[JobCandidate] loaded from DB
    top_candidates: list                # list[JobCandidate] after similarity rank
    final_report_path: str
    error: Optional[str]
