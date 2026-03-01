from fastapi import APIRouter, UploadFile, File
from features.create_functions import create_document
from ai.ai import document_summary
import shutil
import os
import boto3

router = APIRouter(prefix="/document", tags=["document"])


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
    # save image locally temporarily
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    overview = document_summary(file_path)

    document_id = create_document(
        convo_id=convo_id,
        overview=overview,
        content=overview
    )

    return {"document_id": document_id}
