import { useParams } from "@solidjs/router";
import { createSignal } from "solid-js";


export default function FileUploader(props) {
    const [file, setFile] = createSignal();
    const params = useParams();

    const uploadFile = async () => {
        if (!file()) return;
        const formData = new FormData();
        formData.append("files", file());
        console.log("files", file())
        formData.append("folder_id", params.id);
        console.log("folder_id", params.id);
        try {
            const response = await fetch(
                "http://localhost:8888/api/files/upload-files", {
                    method: "POST",
                    body: formData
                }
            )
            const data = await response.json() // return the deck id, notes id, job id etc.
            props.displayUnits(
                (data.file_metadata || []).map(file => ({
                    id: file.storage_id,
                    name: file.name,
                    type: "file",
                    created_at: file.created_at
                }))
            )

            // Generate study units
            const requestBody = JSON.stringify({
                flashcards: {},
                user_id: "23da4be0-70fd-439b-b984-aaf729959e9a",
                folder_id: params.id,
                file_metadata: [
                    {
                        storage_id: data.file_metadata[0].storage_id,
                        extension: data.file_metadata[0].extension
                    }
                ]
            })
            console.log(requestBody)
            const studyUnitsResponse = await fetch(
                "http://localhost:8888/api/files/generate-study-units",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: requestBody
                }
            );
            console.log("studyUnitsResponse", studyUnitsResponse)

            // Get flashcard deck id
            const parsedStudyUnitsResponse = await studyUnitsResponse.json()
            console.log("parsedStudyUnitsResponse", parsedStudyUnitsResponse)

            // Retrieve flashcards
            props.displayUnits([{
                id: parsedStudyUnitsResponse.flashcard_deck_id,
                name: parsedStudyUnitsResponse.name,
                type: "flashcard_deck",
                created_at: parsedStudyUnitsResponse.created_at
            }]);
            console.log("parsedStudyUnitsResponse", parsedStudyUnitsResponse)
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