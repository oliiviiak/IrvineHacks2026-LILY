from fastapi import APIRouter, UploadFile, File
from features.create_functions import create_document
from ai.ai import document_summary
import shutil
import os

router = APIRouter(prefix="/document", tags=["document"])


def upload_to_s3(file_path: str, filename: str) -> str:
    # TODO: replace with real S3 bucket
    # s3 = boto3.client("s3")
    # s3.upload_file(file_path, "bucket name", filename)
    # return f"https://your-bucket-name.s3.amazonaws.com/{filename}"
    return f"placeholder_url/{filename}"


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
