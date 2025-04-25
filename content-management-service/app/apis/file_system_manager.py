from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from ..models import Folder, FlashcardDeck, File
from ..database import get_db

file_system_manager = APIRouter()

class CreateFolderRequest(BaseModel):
    user_id: str
    parent_folder_id: Optional[str] = None
    folder_name: Optional[str] = "New folder"

@file_system_manager.post("/create-folder/")
async def create_folder(request_data: CreateFolderRequest, db: Session = Depends(get_db)):
    try:
        # Count folders with the same name
        parent_folder_id = None
        if request_data.parent_folder_id:
            parent_folder_id = uuid.UUID(request_data.parent_folder_id)
        same_name_folders_num = (
            db.query(func.count(Folder.id))
            .filter(
                Folder.name.op("~")(f"^{request_data.folder_name}(\\s*)(\\d+)?(\\s*)$"),
                Folder.parent_id == parent_folder_id
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
            "folder_id": str(new_folder_id),
            "parent_folder_id": request_data.parent_folder_id,
            "folder_name": folder_name,
            "created_at": new_folder.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        })
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@file_system_manager.post("/delete-folder/")
async def delete_folder(folder_id: str, db: Session = Depends(get_db)):
    try:
        # Get all file storage ids for this folder
        # ...

        # Delete all files from the storage
        # ...

        # Delete folder from db
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
    

@file_system_manager.get("/access-folder/")
async def access_folder(user_id: str, folder_id: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        # Get the folder's subfolders
        folder_id = uuid.UUID(folder_id) if folder_id else None
        subfolder_rows = (
            db.query(Folder.id, Folder.name, Folder.created_at)
            .filter(
                Folder.parent_id == folder_id,
                Folder.user_id == uuid.UUID(user_id)
            )
            .all()
        )
        subfolders = []
        for row in subfolder_rows:
            subfolders.append({
                "id": str(row[0]), 
                "name": row[1], 
                "created_at": str(row[2])
            })

        # Get the folder's flashcard decks
        flashcard_decks_rows = (
            db.query(FlashcardDeck.id, FlashcardDeck.name, FlashcardDeck.created_at)
            .join(
                Folder,
                FlashcardDeck.folder_id == Folder.id
            )
            .filter(
                Folder.id == folder_id,
                Folder.user_id == uuid.UUID(user_id)
            )
            .all()
        )
        flashcard_decks = []
        for row in flashcard_decks_rows:
            flashcard_decks.append({
                "id": str(row[0]), 
                "name": row[1], 
                "created_at": str(row[2])
            })

        # Get the folder's files
        file_rows = (
            db.query(File.id, File.name, File.created_at, File.storage_id)
            .join(
                Folder,
                File.folder_id == Folder.id
            )
            .filter(
                Folder.id == folder_id,
                Folder.user_id == uuid.UUID(user_id)
            )
            .all()
        )
        files = []
        for row in file_rows:
            files.append({
                "id": str(row[0]), 
                "name": row[1], 
                "created_at": str(row[2]),
                "storage_id": str(row[3])
            })
        return JSONResponse(content={
            "subfolders": subfolders,
            "flashcard_decks": flashcard_decks,
            "files": files
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

class FileMetadata(BaseModel):
    storage_id: str
    name: str
    extension: str

class SaveFileNamesRequest(BaseModel):
    file_metadata: List[FileMetadata]
    folder_id: str

@file_system_manager.post("/save-file-names")
async def save_file_names(request_data: SaveFileNamesRequest, db: Session = Depends(get_db)):
    try:
        folder = db.query(Folder).filter_by(id=uuid.UUID(request_data.folder_id)).first()
        if not folder:
            return JSONResponse(content={"msg": "No folder!"}, status_code=404)
        
        for file_meta in request_data.file_metadata:
            folder.files.append(
                File(
                    storage_id=uuid.UUID(file_meta.storage_id),
                    name=file_meta.name,
                    extension=file_meta.extension
                )
            )
        db.commit()
        return JSONResponse(content={"msg": "File names saved!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))