"""
Questions Router
================

API endpoints for agent clarifying questions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from registry import get_project_path
from server.services.agent_questions import (
    get_all_questions,
    get_pending_question,
    add_question,
    answer_question,
    clear_questions,
)

router = APIRouter(prefix="/api/projects/{project_name}/questions", tags=["questions"])


class QuestionCreate(BaseModel):
    """Request body for creating a question."""
    question: str
    context: Optional[str] = None
    options: Optional[list[str]] = None


class AnswerSubmit(BaseModel):
    """Request body for submitting an answer."""
    answer: str


@router.get("")
async def list_questions(project_name: str):
    """Get all questions for a project."""
    project_path = get_project_path(project_name)
    if not project_path:
        raise HTTPException(status_code=404, detail="Project not found")

    questions = get_all_questions(Path(project_path))
    return {"questions": questions}


@router.get("/pending")
async def get_pending(project_name: str):
    """Get the oldest unanswered question."""
    project_path = get_project_path(project_name)
    if not project_path:
        raise HTTPException(status_code=404, detail="Project not found")

    question = get_pending_question(Path(project_path))
    return {"question": question}


@router.post("")
async def create_question(project_name: str, body: QuestionCreate):
    """Create a new question (typically called by agent)."""
    project_path = get_project_path(project_name)
    if not project_path:
        raise HTTPException(status_code=404, detail="Project not found")

    question = add_question(
        Path(project_path),
        question=body.question,
        context=body.context,
        options=body.options,
    )
    return {"question": question}


@router.post("/{question_id}/answer")
async def submit_answer(project_name: str, question_id: str, body: AnswerSubmit):
    """Submit an answer to a question."""
    project_path = get_project_path(project_name)
    if not project_path:
        raise HTTPException(status_code=404, detail="Project not found")

    success = answer_question(Path(project_path), question_id, body.answer)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")

    return {"success": True}


@router.delete("")
async def clear_all_questions(project_name: str):
    """Clear all questions for a project."""
    project_path = get_project_path(project_name)
    if not project_path:
        raise HTTPException(status_code=404, detail="Project not found")

    clear_questions(Path(project_path))
    return {"success": True}
