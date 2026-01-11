"""
Agent Questions Service
=======================

Handles agent clarifying questions and user responses.
Questions are stored in a JSON file in the project directory.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

QUESTIONS_FILE = ".agent_questions.json"


@dataclass
class AgentQuestion:
    """Represents a question from the agent."""
    id: str
    question: str
    context: Optional[str] = None
    options: Optional[list[str]] = None
    timestamp: str = ""
    answered: bool = False
    answer: Optional[str] = None
    answered_at: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


def get_questions_file(project_dir: Path) -> Path:
    """Get the path to the questions file."""
    return project_dir / QUESTIONS_FILE


def load_questions(project_dir: Path) -> list[dict]:
    """Load all questions from the project."""
    questions_file = get_questions_file(project_dir)
    if not questions_file.exists():
        return []
    try:
        with open(questions_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load questions: {e}")
        return []


def save_questions(project_dir: Path, questions: list[dict]) -> None:
    """Save questions to the project."""
    questions_file = get_questions_file(project_dir)
    try:
        with open(questions_file, 'w') as f:
            json.dump(questions, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to save questions: {e}")


def get_pending_question(project_dir: Path) -> Optional[dict]:
    """Get the oldest unanswered question."""
    questions = load_questions(project_dir)
    for q in questions:
        if not q.get('answered', False):
            return q
    return None


def add_question(
    project_dir: Path,
    question: str,
    context: Optional[str] = None,
    options: Optional[list[str]] = None,
) -> AgentQuestion:
    """Add a new question from the agent."""
    questions = load_questions(project_dir)

    # Generate unique ID
    question_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(questions)}"

    new_question = AgentQuestion(
        id=question_id,
        question=question,
        context=context,
        options=options,
    )

    questions.append(asdict(new_question))
    save_questions(project_dir, questions)

    logger.info(f"Added question: {question_id}")
    return new_question


def answer_question(project_dir: Path, question_id: str, answer: str) -> bool:
    """Submit an answer to a question."""
    questions = load_questions(project_dir)

    for q in questions:
        if q.get('id') == question_id:
            q['answered'] = True
            q['answer'] = answer
            q['answered_at'] = datetime.now().isoformat()
            save_questions(project_dir, questions)
            logger.info(f"Answered question: {question_id}")
            return True

    logger.warning(f"Question not found: {question_id}")
    return False


def get_answer(project_dir: Path, question_id: str) -> Optional[str]:
    """Get the answer to a question (for agent to read)."""
    questions = load_questions(project_dir)

    for q in questions:
        if q.get('id') == question_id and q.get('answered'):
            return q.get('answer')

    return None


def clear_questions(project_dir: Path) -> None:
    """Clear all questions."""
    questions_file = get_questions_file(project_dir)
    if questions_file.exists():
        questions_file.unlink()


def parse_question_from_output(line: str) -> Optional[dict]:
    """
    Parse a question from agent output.

    The agent can ask questions using a special format:
    [QUESTION] What color should the button be?
    [QUESTION:OPTIONS] Red,Blue,Green | What color should the button be?
    [QUESTION:CONTEXT] Some context here | What should I do?
    """
    # Simple question
    match = re.match(r'\[QUESTION\]\s*(.+)', line)
    if match:
        return {
            'question': match.group(1).strip(),
            'context': None,
            'options': None,
        }

    # Question with options
    match = re.match(r'\[QUESTION:OPTIONS\]\s*([^|]+)\s*\|\s*(.+)', line)
    if match:
        options = [o.strip() for o in match.group(1).split(',')]
        return {
            'question': match.group(2).strip(),
            'context': None,
            'options': options,
        }

    # Question with context
    match = re.match(r'\[QUESTION:CONTEXT\]\s*([^|]+)\s*\|\s*(.+)', line)
    if match:
        return {
            'question': match.group(2).strip(),
            'context': match.group(1).strip(),
            'options': None,
        }

    return None


def get_all_questions(project_dir: Path) -> list[dict]:
    """Get all questions (answered and unanswered)."""
    return load_questions(project_dir)
