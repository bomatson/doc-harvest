from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from .api import (
    analyze_document_id, test_single_document, test_multiple_documents,
    generate_incremented_ids, test_incremented_documents, get_known_documents,
    test_known_documents, DocumentTestRequest, IncrementRequest
)

app = FastAPI(title="Google Docs Harvester", version="1.0.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Google Docs Harvester API", "status": "running"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

app.post("/analyze/{document_id}")(analyze_document_id)
app.post("/test-document/{document_id}")(test_single_document)
app.post("/test-documents")(test_multiple_documents)
app.post("/generate-increments/{base_id}")(generate_incremented_ids)
app.post("/test-increments")(test_incremented_documents)
app.get("/known-documents")(get_known_documents)
app.post("/test-known-documents")(test_known_documents)
