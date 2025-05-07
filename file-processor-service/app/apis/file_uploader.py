from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
import requests
from uuid import uuid4
import traceback

from .. import CONTENT_MANAGEMENT_SERVICE
from ..tools.claims_extractor import get_user_id_from_jwt


file_uploader = APIRouter()


def save_file_to_storage(file, unique_name):
    file_path = os.path.join("files", unique_name)
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

@file_uploader.post("/upload-files")
async def upload_files(
    files: List[UploadFile] = File(...), 
    folder_id: Optional[str] = Form(...),
    user_id: str = Depends(get_user_id_from_jwt)
):
    try:
        folder_id = folder_id if folder_id != "home" else user_id
        uploaded_files = []
        for file in files:
            try:
                file_id = str(uuid4())
                _, extension = os.path.splitext(file.filename)
                save_file_to_storage(file, file_id + extension)
                extension = extension.lstrip(".")
                uploaded_files.append({
                    "file_id": file_id,
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
    

@file_uploader.get("/file")
async def get_file(file_id: str):
    # Construct the safe file path
    file_path = os.path.join("files", f"{file_id}.pdf")
    
    # Check if the file exists before serving it
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Return the file response
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{file_id}.pdf"
    )