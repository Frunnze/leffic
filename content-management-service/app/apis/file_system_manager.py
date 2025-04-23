from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Folder
from ..database import get_db

file_system_manager = APIRouter()

class CreateFolderRequest(BaseModel):
    user_id: str
    parent_folder_id: Optional[str] = None
    folder_name: Optional[str] = "New folder"

@file_system_manager.post("/create-folder")
async def create_folder(request_data: CreateFolderRequest, db: Session = Depends(get_db)):
    try:
        # Count folders with the same name
        same_name_folders_num = (
            db.query(func.count(Folder.id))
            .filter(
                Folder.name == request_data.folder_name,
                Folder.parent_id == uuid.UUID(request_data.parent_folder_id)
            )
            .scalar()
        )

        # Set the name
        if same_name_folders_num and same_name_folders_num > 0:
            folder_name = request_data.folder_name + " " + str(same_name_folders_num+1)
        else:
            folder_name = request_data.folder_name 

        # Create the row
        new_folder = Folder(
            parent_id=uuid.UUID(request_data.parent_folder_id) if request_data.parent_folder_id else None,
            name=folder_name,
            user_id=uuid.UUID(request_data.user_id)
        )
        db.add(new_folder)
        db.flush()
        new_folder_id = new_folder.id
        db.commit()
        return JSONResponse(content={
            "folder_id": new_folder_id,
            "parent_folder_id": new_folder.parent_id,
            "folder_name": folder_name,
            "created_at": new_folder.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        })
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@file_system_manager.post("/delete-folder")
async def delete_folder(folder_id: str, db: Session = Depends(get_db)):
    try:
        folder = (
            db.query(Folder)
            .filter_by(id=uuid.UUID(folder_id))
            .first()
        )
        db.delete(folder)
        db.commit()
        return JSONResponse(content={"msg": "Folder deleted!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@file_system_manager.post("/access-folder")
async def access_folder(folder_id: str, db: Session = Depends(get_db)):
    try:
        pass
        return JSONResponse(content={"msg": "msg!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))