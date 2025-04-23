from fastapi import APIRouter, File, UploadFile
from typing import List
import os
import shutil
from uuid import uuid4

file_uploader = APIRouter()


def save_file_to_storage(file, unique_name):
    file_path = os.path.join("files", unique_name)
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

@file_uploader.post("/upload-files/")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_files = []

    for file in files:
        try:
            unique_name = f"{uuid4().hex}_{file.filename}"
            save_file_to_storage(file, unique_name)
            uploaded_files.append(unique_name)
        except Exception as e:
            return {"error": f"Failed to upload {file.filename}: {str(e)}"}

    return {"msg": "Files uploaded successfully", "files": uploaded_files}