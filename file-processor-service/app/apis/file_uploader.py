from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import List, Optional
import os
import shutil
import requests
from uuid import uuid4
import traceback

from .. import CONTENT_MANAGEMENT_SERVICE


file_uploader = APIRouter()


def save_file_to_storage(file, unique_name):
    file_path = os.path.join("files", unique_name)
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

@file_uploader.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...), folder_id: Optional[str] = Form(...)):
    try:
        uploaded_files = []

        for file in files:
            try:
                storage_id = str(uuid4())
                _, extension = os.path.splitext(file.filename)
                save_file_to_storage(file, storage_id + extension)
                extension = extension.lstrip(".")
                uploaded_files.append({
                    "storage_id": storage_id,
                    "extension": extension,
                    "name": file.filename
                })
            except Exception as e:
                return {"error": f"Failed to upload {file.filename}: {str(e)}"}

        # Save the file names
        response = requests.post(
            url=CONTENT_MANAGEMENT_SERVICE + "/save-file-names",
            json={
                "file_metadata": uploaded_files,
                "folder_id": folder_id
            }
        )
        print(response.json())
        response.raise_for_status()

        return {"msg": "Files uploaded!", "file_metadata": uploaded_files}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))