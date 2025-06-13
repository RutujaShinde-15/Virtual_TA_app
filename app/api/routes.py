from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, Dict, Any
import base64
from app.core.rag import RAGEngine
from app.core.gemini import GeminiProcessor
from app.models.schemas import QuestionResponse, QuestionRequest

router = APIRouter()
rag_engine = RAGEngine()
gemini_processor = GeminiProcessor()

@router.post("/", response_model=QuestionResponse)
async def answer_question(
    question: str = Form(...),
    image: Optional[UploadFile] = File(None)
) -> Dict[str, Any]:
    """
    Answer a student's question using RAG and Gemini.
    
    Args:
        question: The student's question
        image: Optional image attachment
    
    Returns:
        Dict containing answer and relevant links
    """
    try:
        # Process image if provided
        image_base64 = None
        if image:
            contents = await image.read()
            image_base64 = base64.b64encode(contents).decode()
        
        # Get answer using RAG
        answer, links = rag_engine.get_answer(question, image_base64)
        
        return {
            "answer": answer,
            "links": links
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/json/", response_model=QuestionResponse)
async def answer_question_json(request: QuestionRequest) -> Dict[str, Any]:
    """
    Answer a student's question using RAG and Gemini (JSON endpoint).
    Args:
        request: QuestionRequest with question and optional image (base64 or file path)
    Returns:
        Dict containing answer and relevant links
    """
    try:
        question = request.question
        image_base64 = request.image
        answer, links = rag_engine.get_answer(question, image_base64)
        return {
            "answer": answer,
            "links": links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 