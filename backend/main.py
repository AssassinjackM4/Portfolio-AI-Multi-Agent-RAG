import hashlib
import logging
import os
import re
from functools import lru_cache
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from groq import APIConnectionError, APIError, APIStatusError, Groq
from pydantic import BaseModel, Field
from pypdf import PdfReader

from agents import AGENTS, route_question
from rag.resume_chunks import chunk_resume

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR = UPLOAD_DIR / ".chroma"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
MAX_QUESTION_LENGTH = 2000
RETRIEVAL_INDEX_VERSION = "section-aware-v2"
RETRIEVAL_STOP_WORDS = {
    "a",
    "about",
    "and",
    "are",
    "candidate",
    "did",
    "does",
    "for",
    "he",
    "his",
    "how",
    "i",
    "in",
    "is",
    "me",
    "of",
    "the",
    "their",
    "them",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "with",
    "you",
}
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
logger = logging.getLogger(__name__)


def get_allowed_origins() -> list[str]:
    configured_origins = [
        os.getenv(
            "FRONTEND_URL",
            "https://portfolio-ai-multi-agent-rag.vercel.app",
        ),
        *os.getenv("FRONTEND_ORIGINS", "").split(","),
    ]
    origins = {
        origin.strip().rstrip("/")
        for origin in configured_origins
        if origin.strip()
    }
    return sorted(
        origins
        | {
            "http://localhost:3000",
            "http://localhost:5173",
            "https://portfolio-ai-frontend.vercel.app",
        }
    )


app = FastAPI(title="Portfolio AI API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    resume_file: str | None = None


def resolve_resume_path(resume_file: str | None = None) -> Path:
    if resume_file:
        filename = Path(resume_file.replace("\\", "/")).name
        if not filename or filename in {".", ".."}:
            raise FileNotFoundError("The selected resume file is invalid.")
        candidate = (UPLOAD_DIR / filename).resolve()
        if candidate.parent != UPLOAD_DIR.resolve() or not candidate.is_file():
            raise FileNotFoundError("The selected resume file was not found.")
        return candidate

    for path in (BASE_DIR / "my_resume.pdf", UPLOAD_DIR / "my_resume.pdf"):
        if path.is_file():
            return path.resolve()

    raise FileNotFoundError("No resume file found. Please upload a PDF resume first.")


def read_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    return "\n".join(
        page_text.strip()
        for page in reader.pages
        if (page_text := page.extract_text())
    ).strip()


@lru_cache(maxsize=1)
def get_vector_db():
    return chromadb.PersistentClient(path=str(VECTOR_DB_DIR))


def _retrieval_terms(text: str) -> set[str]:
    terms = set(re.findall(r"[a-z0-9+#.]+", text.casefold()))
    return {
        term[:-3] + "y"
        if term.endswith("ies")
        else term[:-1]
        if term.endswith("s") and len(term) > 3
        else term
        for term in terms - RETRIEVAL_STOP_WORDS
    }


def retrieve_resume_chunks(resume_text: str, question: str) -> list[dict[str, str]]:
    chunks = chunk_resume(resume_text)
    if not chunks:
        return []

    content_key = hashlib.sha256(
        f"{RETRIEVAL_INDEX_VERSION}\0{resume_text}".encode("utf-8")
    ).hexdigest()
    collection_name = f"resume_{content_key[:24]}"
    collection = get_vector_db().get_or_create_collection(name=collection_name)

    if collection.count() == 0:
        collection.add(
            ids=[f"chunk_{index}" for index in range(len(chunks))],
            documents=[
                f"[{chunk['section']}] {chunk['content']}" for chunk in chunks
            ],
            metadatas=[{"section": chunk["section"]} for chunk in chunks],
        )

    results = collection.query(
        query_texts=[question],
        n_results=min(12, len(chunks)),
        include=["documents", "metadatas", "distances"],
    )
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []
    query_terms = _retrieval_terms(question)
    return _rank_retrieval_results(documents, metadatas, distances, query_terms)


def _rank_retrieval_results(
    documents: list[str],
    metadatas: list[dict[str, str]],
    distances: list[float],
    query_terms: set[str],
) -> list[dict[str, str]]:
    ranked_sources = []
    matching_sources = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        section = metadata["section"]
        prefix = f"[{section}] "
        content = document.removeprefix(prefix)
        overlap = len(query_terms & _retrieval_terms(f"{section} {content}"))
        score = distance - (0.25 * overlap / len(query_terms)) if query_terms else distance
        source = (score, section, content)
        ranked_sources.append(source)
        if overlap:
            matching_sources.append(source)

    if matching_sources:
        ranked_sources = matching_sources
    return [
        {"section": section, "content": content}
        for _, section, content in sorted(ranked_sources)[:3]
    ]


def generate_answer(question: str, agent_id: str, sources: list[dict[str, str]]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured on the backend.",
        )

    agent = AGENTS[agent_id]
    context = "\n\n".join(
        f"[{source['section']}]\n{source['content']}" for source in sources
    )
    system_prompt = f"""You are a {agent['role']} representing the job candidate in this portfolio.
{agent['instructions']}

Use only the resume excerpts below. Do not infer or invent experience, skills,
availability, career goals, or contact details. If the excerpts do not answer the
question, say: "I don't have enough information in the resume to answer that."
Be professional, specific, and concise. Refer to relevant section names in your
answer when useful.

RESUME EXCERPTS:
{context or "No relevant resume excerpts were found."}
"""

    try:
        response = Groq(api_key=api_key).chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question.strip()},
            ],
        )
    except APIError as error:
        logger.exception("Groq answer generation failed")
        if isinstance(error, APIStatusError):
            if error.status_code in {401, 403}:
                detail = "AI provider authentication failed. Check GROQ_API_KEY in the backend environment."
            elif error.status_code == 404:
                detail = "The configured AI model was not found. Check GROQ_MODEL in the backend environment."
            elif error.status_code == 429:
                detail = "The AI provider rate limit or quota was reached. Check your Groq account limits and try again."
            else:
                detail = (
                    f"The AI provider request failed with HTTP {error.status_code}. "
                    "Check backend logs and provider status."
                )
        elif isinstance(error, APIConnectionError):
            detail = "Could not reach the AI provider. Check backend network access and try again."
        else:
            detail = "The AI provider request failed. Check backend logs and try again."
        raise HTTPException(
            status_code=502,
            detail=detail,
        ) from error

    answer = response.choices[0].message.content
    if not answer:
        raise HTTPException(status_code=502, detail="The AI provider returned an empty answer.")
    return answer


@app.get("/")
def home():
    return {
        "message": "Portfolio AI backend is running.",
        "status": "healthy",
        "features": ["retrieval-augmented generation", "supervisor-routed specialist agents"],
        "agents": [
            {"id": agent_id, "name": agent["name"]}
            for agent_id, agent in AGENTS.items()
        ],
        "endpoints": {
            "chat": "POST /chat",
            "upload_resume": "POST /upload-resume",
            "health": "GET /",
        },
    }


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resume files are supported.")

    content = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Resume files must be 10 MB or smaller.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    filename = Path(file.filename.replace("\\", "/")).name
    filename = re.sub(r"[^A-Za-z0-9._-]+", "_", filename)
    if not filename or filename in {".", ".."}:
        raise HTTPException(status_code=400, detail="The uploaded filename is invalid.")

    save_path = UPLOAD_DIR / filename
    save_path.write_bytes(content)
    return {
        "message": "Resume uploaded successfully.",
        "filename": save_path.name,
        "status": "uploaded",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be blank.")

    try:
        resume_path = resolve_resume_path(request.resume_file)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured on the backend.",
        )

    try:
        resume_text = read_pdf(resume_path)
    except Exception as error:
        logger.exception("Could not read resume PDF: %s", resume_path.name)
        raise HTTPException(status_code=422, detail="The selected resume could not be read as a PDF.") from error

    if not resume_text:
        raise HTTPException(status_code=422, detail="The selected PDF contains no extractable text.")

    agent_id = route_question(request.question)
    try:
        sources = retrieve_resume_chunks(resume_text, request.question.strip())
    except Exception as error:
        logger.exception("Resume retrieval failed")
        raise HTTPException(
            status_code=503,
            detail="Resume retrieval is unavailable. Check the backend logs and try again.",
        ) from error

    answer = generate_answer(request.question, agent_id, sources)
    return {
        "answer": answer,
        "agent": agent_id,
        "agent_name": AGENTS[agent_id]["name"],
        "sources": [
            {"section": source["section"], "excerpt": source["content"]}
            for source in sources
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
