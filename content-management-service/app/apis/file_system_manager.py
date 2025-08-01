from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session, aliased
import os

from ..models import Folder, FlashcardDeck, File, Note, Test
from ..database import get_db
from ..tools.claims_extractor import get_user_id_from_jwt

file_system_manager = APIRouter()

class CreateFolderRequest(BaseModel):
    parent_folder_id: Optional[str] = None
    folder_name: Optional[str] = "New folder"

@file_system_manager.post("/create-folder")
async def create_folder(request_data: CreateFolderRequest, user_id: str = Depends(get_user_id_from_jwt), db: Session = Depends(get_db)):
    try:
        parent_folder_id = request_data.parent_folder_id if request_data.parent_folder_id != "home" else user_id
        # Count folders with the same name
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
            parent_id=parent_folder_id,
            name=folder_name,
            user_id=uuid.UUID(user_id),
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_folder)
        db.flush()
        new_folder_id = new_folder.id
        db.commit()
        return JSONResponse(content={
            "folder_id": str(new_folder_id),
            "parent_folder_id": parent_folder_id,
            "folder_name": folder_name,
            "created_at": new_folder.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        })
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def delete_file_from_storage(filename):
    if os.path.exists("files" + "/" + filename):
        os.remove("files" + "/" + filename)
        print("File deleted successfully.")
    else:
        print("File does not exist.")

@file_system_manager.delete("/delete-folder/")
async def delete_folder(folder_id: str, db: Session = Depends(get_db)):
    try:
        folder = (
            db.query(Folder)
            .filter_by(id=folder_id)
            .first()
        )

        files_storage_ids = []
        folder_cte = (
            select(Folder.id)
            .where(Folder.id == folder_id)
            .cte(name="subfolders", recursive=True)
        )
        subfolder = aliased(Folder)
        folder_cte = folder_cte.union_all(
            select(subfolder.id).where(subfolder.parent_id == folder_cte.c.id)
        )
        files = (
            db.query(File)
            .where(File.folder_id.in_(folder_cte))
            .all()
        )
        for file in files:
            files_storage_ids.append(str(file.id) + "." + file.extension)

        # Delete the main folder
        db.delete(folder)
        db.commit()

        # Delete the files
        for file_storage_id in files_storage_ids:
            delete_file_from_storage(file_storage_id)

        return JSONResponse(content={"msg": "Folder deleted!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@file_system_manager.get("/access-folder/")
async def access_folder(
    folder_id: Optional[str] = None,
    user_id: str = Depends(get_user_id_from_jwt), 
    db: Session = Depends(get_db)
):
    try:
        parent_folder_name = None
        if folder_id == "home":
            folder = db.query(Folder).filter_by(id=user_id).first()
            if folder is None:
                folder = Folder(
                    id=uuid.UUID(user_id),
                    name="Home",
                    user_id=uuid.UUID(user_id)
                )
                db.add(folder)
                db.commit()
                return JSONResponse(content={
                    "content": [],
                    "parent_folder_name": "Home"
                })
            folder_id = folder.id
            parent_folder_name = folder.name
        else:
            folder = db.query(Folder).filter_by(id=folder_id).first()
            parent_folder_name = folder.name if folder else "Home"

        content = []
        subfolder_rows = (
            db.query(Folder)
            .filter(
                Folder.parent_id == folder_id,
                Folder.user_id == uuid.UUID(user_id)
            )
            .all()
        )
        for row in subfolder_rows:
            content.append({
                "id": str(row.id),
                "name": row.name, 
                "created_at": str(row.created_at),
                "type": "folder"
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
        for row in flashcard_decks_rows:
            content.append({
                "id": str(row[0]), 
                "name": row[1], 
                "created_at": str(row[2]),
                "type": "flashcard_deck"
            })

        # Get the folder's flashcard tests
        test_rows = (
            db.query(Test.id, Test.name, Test.created_at)
            .join(
                Folder,
                Test.folder_id == Folder.id
            )
            .filter(
                Folder.id == folder_id,
                Folder.user_id == uuid.UUID(user_id)
            )
            .all()
        )
        for row in test_rows:
            content.append({
                "id": str(row[0]), 
                "name": row[1], 
                "created_at": str(row[2]),
                "type": "test"
            })

        # Get the folder's files
        file_rows = (
            db.query(File.id, File.name, File.created_at, File.extension)
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
        for row in file_rows:
            content.append({
                "id": str(row[0]), 
                "name": row[1], 
                "created_at": str(row[2]),
                "extension": str(row[3]),
                "type": "file"
            })

        # Get the folder's files
        notes_rows = (
            db.query(Note.id, Note.name, Note.created_at)
            .filter(Note.folder_id == folder_id)
            .all()
        )
        for row in notes_rows:
            content.append({
                "id": str(row[0]), 
                "name": row[1], 
                "created_at": str(row[2]),
                "type": "note"
            })
        return JSONResponse(content={
            "content": content,
            "parent_folder_name": parent_folder_name
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

class FileMetadata(BaseModel):
    file_id: str
    name: str
    extension: str

class SaveFileNamesRequest(BaseModel):
    file_metadata: List[FileMetadata]
    folder_id: Optional[str] = None

@file_system_manager.post("/save-file-names")
async def save_file_names(request_data: SaveFileNamesRequest, db: Session = Depends(get_db)):
    try:
        folder = db.query(Folder).filter_by(id=request_data.folder_id).first()
        if not folder:
            folder = Folder(
                name=request_data.file_metadata[0].name,
            )
        
        for file_meta in request_data.file_metadata:
            folder.files.append(
                File(
                    id=file_meta.file_id,
                    name=file_meta.name,
                    extension=file_meta.extension
                )
            )
        db.commit()
        return JSONResponse(content={"msg": "File names saved!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@file_system_manager.delete("/delete-deck/")
async def delete_deck(deck_id: str, db: Session = Depends(get_db)):
    try:
        deck = (
            db.query(FlashcardDeck)
            .filter_by(id=deck_id)
            .first()
        )
        db.delete(deck)
        db.commit()
        return JSONResponse(content={"msg": "Deck deleted!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@file_system_manager.delete("/delete-test/")
async def delete_test(test_id: str, db: Session = Depends(get_db)):
    try:
        test = (
            db.query(Test)
            .filter_by(id=test_id)
            .first()
        )
        db.delete(test)
        db.commit()
        return JSONResponse(content={"msg": "Test deleted!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@file_system_manager.delete("/delete-note/")
async def delete_test(note_id: str, db: Session = Depends(get_db)):
    try:
        note = (
            db.query(Note)
            .filter_by(id=note_id)
            .first()
        )
        db.delete(note)
        db.commit()
        return JSONResponse(content={"msg": "Note deleted!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@file_system_manager.delete("/delete-file/")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    try:
        file = (
            db.query(File)
            .filter_by(id=file_id)
            .first()
        )
        file_storage_id = str(file.id) + "." + file.extension
        db.delete(file)
        db.commit()
        delete_file_from_storage(file_storage_id)
        return JSONResponse(content={"msg": "File deleted!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))