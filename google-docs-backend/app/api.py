"""
FastAPI endpoints for Google Docs harvesting
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from .document_analyzer import GoogleDocsAnalyzer, DocumentInfo

app = FastAPI(title="Google Docs Harvester API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = GoogleDocsAnalyzer()

class DocumentTestRequest(BaseModel):
    document_ids: List[str]
    delay: float = 1.0

class IncrementRequest(BaseModel):
    base_id: str
    strategies: List[str] = ["last_char", "last_digit", "last_letter", "pattern_based"]
    max_increments: int = 10
    test_delay: float = 1.0

class DocumentResponse(BaseModel):
    id: str
    url: str
    accessible: bool
    title: Optional[str] = None
    content_preview: Optional[str] = None
    content_hash: Optional[str] = None
    error: Optional[str] = None

class AnalysisResponse(BaseModel):
    document_id: str
    length: int
    character_counts: Dict[str, int]
    patterns: Dict
    has_hyphens: bool
    has_underscores: bool
    alphanumeric_only: bool
    starts_with_digit: bool

@app.get("/")
async def root():
    return {"message": "Google Docs Harvester API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "analyzer": "ready"}

@app.post("/analyze/{document_id}")
async def analyze_document_id(document_id: str) -> AnalysisResponse:
    """Analyze the structure of a document ID"""
    try:
        analysis = analyzer.analyze_id_structure(document_id)
        return AnalysisResponse(
            document_id=document_id,
            length=analysis["length"],
            character_counts=analysis["character_counts"],
            patterns=analysis["pattern_analysis"],
            has_hyphens=analysis["has_hyphens"],
            has_underscores=analysis["has_underscores"],
            alphanumeric_only=analysis["alphanumeric_only"],
            starts_with_digit=analysis["starts_with_digit"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/test-document/{document_id}")
async def test_single_document(document_id: str) -> DocumentResponse:
    """Test if a single document ID is accessible"""
    try:
        doc_info = await analyzer.test_document_access(document_id)
        return DocumentResponse(
            id=doc_info.id,
            url=doc_info.url,
            accessible=doc_info.accessible,
            title=doc_info.title,
            content_preview=doc_info.content_preview,
            content_hash=doc_info.content_hash,
            error=doc_info.error
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document test failed: {str(e)}")

@app.post("/test-documents")
async def test_multiple_documents(request: DocumentTestRequest) -> List[DocumentResponse]:
    """Test multiple document IDs with rate limiting"""
    try:
        results = await analyzer.batch_test_documents(request.document_ids, request.delay)
        return [
            DocumentResponse(
                id=doc.id,
                url=doc.url,
                accessible=doc.accessible,
                title=doc.title,
                content_preview=doc.content_preview,
                content_hash=doc.content_hash,
                error=doc.error
            )
            for doc in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch test failed: {str(e)}")

@app.post("/generate-increments/{base_id}")
async def generate_incremented_ids(base_id: str, strategies: Optional[List[str]] = None) -> Dict:
    """Generate incremented versions of a document ID"""
    try:
        if strategies is None:
            strategies = ["last_char", "last_digit", "last_letter"]
        
        incremented_ids = analyzer.generate_incremented_ids(base_id, strategies)
        return {
            "base_id": base_id,
            "strategies": strategies,
            "incremented_ids": incremented_ids,
            "count": len(incremented_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ID generation failed: {str(e)}")

@app.post("/test-increments")
async def test_incremented_documents(request: IncrementRequest) -> Dict:
    """Generate and test incremented document IDs"""
    try:
        incremented_ids = analyzer.generate_incremented_ids(
            request.base_id, 
            request.strategies
        )[:request.max_increments]
        
        results = await analyzer.batch_test_documents(incremented_ids, request.test_delay)
        
        successful = [r for r in results if r.accessible]
        failed = [r for r in results if not r.accessible]
        
        uniqueness_analysis = analyzer.analyze_uniqueness(results)
        
        return {
            "base_id": request.base_id,
            "strategies": request.strategies,
            "total_tested": len(results),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "unique_documents_count": uniqueness_analysis["unique_count"],
            "duplicate_documents_count": uniqueness_analysis["duplicate_count"],
            "uniqueness_rate": uniqueness_analysis["uniqueness_rate"],
            "successful_documents": [
                DocumentResponse(
                    id=doc.id,
                    url=doc.url,
                    accessible=doc.accessible,
                    title=doc.title,
                    content_preview=doc.content_preview,
                    content_hash=doc.content_hash,
                    error=doc.error
                )
                for doc in successful
            ],
            "failed_documents": [
                DocumentResponse(
                    id=doc.id,
                    url=doc.url,
                    accessible=doc.accessible,
                    title=doc.title,
                    content_preview=doc.content_preview,
                    content_hash=doc.content_hash,
                    error=doc.error
                )
                for doc in failed
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Increment test failed: {str(e)}")

@app.get("/known-documents")
async def get_known_documents() -> List[str]:
    """Get the list of known working document IDs"""
    return analyzer.known_ids

@app.post("/test-known-documents")
async def test_known_documents() -> List[DocumentResponse]:
    """Test all known document IDs"""
    try:
        results = await analyzer.batch_test_documents(analyzer.known_ids)
        return [
            DocumentResponse(
                id=doc.id,
                url=doc.url,
                accessible=doc.accessible,
                title=doc.title,
                content_preview=doc.content_preview,
                content_hash=doc.content_hash,
                error=doc.error
            )
            for doc in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Known documents test failed: {str(e)}")

@app.post("/analyze-uniqueness")
async def analyze_document_uniqueness(request: DocumentTestRequest) -> Dict:
    """Analyze uniqueness of a set of document IDs"""
    try:
        results = await analyzer.batch_test_documents(request.document_ids, request.delay)
        uniqueness_analysis = analyzer.analyze_uniqueness(results)
        return uniqueness_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Uniqueness analysis failed: {str(e)}")
