import { useParams } from "@solidjs/router";
import { createEffect, createSignal } from "solid-js";
import { useNotificationContext } from "../context/NotificationContext";
import { apiRequest } from "../utils/apiRequest";


export default function FileUploader(props) {
    const [file, setFile] = createSignal();
    const [flashcardsGenerationTaskId, setFlashcardsGenerationTaskId] = createSignal();
    const [noteGenerationTaskId, setNoteGenerationTaskId] = createSignal();
    const [folderId, setFolderId] = createSignal();
    const {
        setDisplayStartGenerationNotification, 
        setFlashcardsTaskStatus,
        setNoteTaskStatus
    } = useNotificationContext();

    const params = useParams();

    async function generateStudyUnits(file_id, extension) {
        const flashcardsGenerationResponse = await apiRequest({
            endpoint: "/api/files/generate-study-units",
            method: "POST",
            body: {
                flashcards: {},
                folder_id: params.id,
                file_metadata: [
                    {
                        file_id: file_id,
                        extension: extension
                    }
                ]
            }
        })
        const studyUnitsGenerationResponseData = await flashcardsGenerationResponse.json()
        setFlashcardsGenerationTaskId(studyUnitsGenerationResponseData.task_id)
        setNoteGenerationTaskId(studyUnitsGenerationResponseData.note_task_id)
        setDisplayStartGenerationNotification(true);
    }

    // Check the flashcards generation task
    createEffect(() => {
        if (!flashcardsGenerationTaskId()) return;
        const interval = setInterval(async () => {
          try {
            const res = await apiRequest({
                endpoint: `/api/files/flashcards-status/${flashcardsGenerationTaskId()}`
            })
            const data = await res.json();
            setFlashcardsTaskStatus(data.status)
            console.log("FLASHCARDS GENERATION TASK STATUS", data)
            
            if (data.status === "SUCCESS" && params.id === folderId()) {
                props.displayUnits([{
                    id: data.flashcard_deck_id,
                    name: data.name,
                    type: data.type,
                    created_at: data.created_at
                }]);
            }
            if (data.status === "SUCCESS" || data.status === "FAILURE") {
              clearInterval(interval); // stop polling
              setFlashcardsGenerationTaskId(null);
            }
          } catch (err) {
            console.error("Error polling task status:", err);
          }
        }, 2000);
      
        // Cleanup on component unmount or task ID change
        return () => clearInterval(interval);
      });

    // Check the note generation task
    createEffect(() => {
        if (!noteGenerationTaskId()) return;
        const interval = setInterval(async () => {
            try {
                const res = await apiRequest({
                    endpoint: `/api/files/note-task-status/${noteGenerationTaskId()}`
                })
                const data = await res.json();
                setNoteTaskStatus(data.status)
                console.log("NOTE GENERATION TASK STATUS", data)
                
                if (data.status === "SUCCESS" && params.id === folderId()) {
                    props.displayUnits([{
                        id: data.note_id,
                        name: data.name,
                        type: data.type,
                        created_at: data.created_at
                    }]);
                }
                if (data.status === "SUCCESS" || data.status === "FAILURE") {
                    clearInterval(interval); // stop polling
                    setNoteGenerationTaskId(null);
                }
            } catch (err) {
                console.error("Error polling task status:", err);
            }
        }, 2000);        
        return () => clearInterval(interval);
        });

    const uploadFile = async () => {
        if (!file()) return;
        const formData = new FormData();
        formData.append("files", file());
        formData.append("folder_id", params.id);
        setFolderId(params.id)
        try {
            const response = await apiRequest({
                endpoint: "/api/files/upload-files",
                method: "POST",
                body: formData
            })
            const data = await response.json()
            props.displayUnits(
                (data.file_metadata || []).map(file => ({
                    id: file.file_id,
                    name: file.name,
                    type: "file",
                    created_at: file.created_at
                }))
            )

            // Generate flashcards
            await generateStudyUnits(data.file_metadata[0].file_id, data.file_metadata[0].extension)
        } catch (error) {
            console.error("Error: ", error);
        };
    };

    const handleFileChange = (e) => {
        const target = e.target;
        const selectedFile = target.files?.[0] || null;
        setFile(selectedFile);
        if (selectedFile) {
            uploadFile();
        }
    };

    return (
        <label class="btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 18 18" fill="none">
                <g clip-path="url(#clip0_5_7)">
                <path d="M7.93377 13.5V4.33125L4.98694 7.25625L3.40019 5.625L9.06716 0L14.7341 5.625L13.1474 7.25625L10.2006 4.33125V13.5H7.93377ZM2.26679 18C1.64342 18 1.10978 17.7797 0.66587 17.3391C0.221957 16.8984 0 16.3687 0 15.75V12.375H2.26679V15.75H15.8675V12.375H18.1343V15.75C18.1343 16.3687 17.9124 16.8984 17.4685 17.3391C17.0245 17.7797 16.4909 18 15.8675 18H2.26679Z" fill="#39393A"/>
                </g>
                <defs>
                <clipPath id="clip0_5_7">
                <rect width="18" height="18" fill="white"/>
                </clipPath>
                </defs>
            </svg>
            <input type="file" class="hidden" onChange={handleFileChange}/>
            <span>AI Import</span>
        </label>
    );
}