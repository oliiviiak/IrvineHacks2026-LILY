# backend/routes/document.py
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File
from features.create_functions import create_document
from ai.ai import document_summary
from db.db import db
import shutil
import os
import boto3

router = APIRouter(prefix="/document", tags=["document"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")


def upload_to_s3(file_path: str, filename: str) -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    s3.upload_file(file_path, bucket_name, filename)

    return f"https://{bucket_name}.s3.amazonaws.com/{filename}"


@router.post("/")
async def upload_document(convo_id: str, file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    s3_url = upload_to_s3(file_path, str(uuid.uuid4()))  # ← was missing
    overview = document_summary(file_path)

    document_id = create_document(
        convo_id=convo_id,
        overview=overview,
        content=overview,
        url=s3_url,              # ← was saving local path
    )

    return {"document_id": document_id, "overview": overview}


@router.get("/{document_id}")
def get_document(document_id: str):
    row = db.execute(
        "SELECT * FROM documents WHERE document_id = ?", (document_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    return dict(row)