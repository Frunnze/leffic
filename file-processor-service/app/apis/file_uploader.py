from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse, Response
from typing import List, Optional
import os
import shutil
import requests
from uuid import uuid4
import traceback
import pyclamd
import shutil
import subprocess
import tempfile


from .. import CONTENT_MANAGEMENT_SERVICE
from ..tools.claims_extractor import get_user_id_from_jwt


file_uploader = APIRouter()


def save_file_to_storage(file, unique_name):
    file_path = os.path.join("files", unique_name)
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)


def scan_file_in_memory(file: UploadFile):
    cd = pyclamd.ClamdNetworkSocket()
    if not cd.ping():
        raise RuntimeError("Could not connect to ClamAV daemon")
    file.file.seek(0)
    result = cd.instream(file.file)
    file.file.seek(0)
    return result
    

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
                # scan_result = scan_file_in_memory(file)
                # if scan_result:
                #     raise HTTPException(status_code=400, detail=f"Malicious file detected: {scan_result}")

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
async def get_file(file_id: str, file_extension: str):
    input_path = os.path.join("files", f"{file_id}.{file_extension}")

    if os.path.exists(input_path):
        if file_extension == "pdf":
            return FileResponse(
                path=input_path,
                media_type="application/pdf",
                filename=f"{file_id}.pdf"
            )
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = subprocess.run([
                    "libreoffice", "--headless", "--convert-to", "pdf",
                    "--outdir", tmp_dir, input_path
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if result.returncode != 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Conversion failed: {result.stderr.decode()}"
                    )

                temp_pdf_path = os.path.join(tmp_dir, f"{file_id}.pdf")
                with open(temp_pdf_path, "rb") as f:
                    pdf_content = f.read()

            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={file_id}.pdf"
                }
            )

    raise HTTPException(status_code=404, detail="File not found")