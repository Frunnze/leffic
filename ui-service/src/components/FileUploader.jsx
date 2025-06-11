import { useParams } from "@solidjs/router";
import { createSignal } from "solid-js";
import { apiRequest } from "../utils/apiRequest";
import FailureNotification from "./notifications/FailureNotification";


export default function FileUploader(props) {
    const [file, setFile] = createSignal();
    const [fileTooLargeNotification, setFileTooLargeNotification] = createSignal(false);
    const [maliciousFileNotification, setMaliciousFileNotification] = createSignal(false);
    const params = useParams();

    const uploadFile = async () => {
        if (!file()) return;
        const formData = new FormData();
        formData.append("files", file());
        formData.append("folder_id", params.id);
        try {
            const response = await apiRequest({
                endpoint: "/api/files/upload-files",
                method: "POST",
                body: formData
            })
            if (response.status === 403) {
                setMaliciousFileNotification(true);
                return;
            }
            const data = await response.json()
            props.displayUnits(
                (data.file_metadata || []).map(file => ({
                    id: file.file_id,
                    name: file.name,
                    extension: file.extension,
                    type: "file",
                    created_at: file.created_at
                }))
            )

            // Generate
            await props.generateStudyUnits(
                {
                    note: {},
                    test: {},
                    flashcards: {},
                    folder_id: params.id,
                    file_metadata: [
                        {
                            file_id: data.file_metadata[0].file_id,
                            extension: data.file_metadata[0].extension
                        }
                    ]
                }
            );
        } catch (error) {
            console.error("Error: ", error);
        };
    };

    const handleFileChange = (e) => {
        const target = e.target;
        const selectedFile = target.files?.[0] || null;

        // Check file's size
        if (selectedFile) {
            const sizeInMB = selectedFile.size / (1024 * 1024);
            if (sizeInMB > 100) {
                setFileTooLargeNotification(true);
                return;
            }
            setFile(selectedFile);
            uploadFile();
        };
    };

    return (
        <>
            <Show when={fileTooLargeNotification()}>
                <FailureNotification 
                    closeNotification={() => setFileTooLargeNotification(false)}
                    primaryLabel="Error"
                    secondaryLabel="File is too large. Please select a file under 100 MB."
                />
            </Show>

            <Show when={maliciousFileNotification()}>
                <FailureNotification 
                    closeNotification={() => setMaliciousFileNotification(false)}
                    primaryLabel="Warning"
                    secondaryLabel="This file contains malicious content."
                />
            </Show>
            
            <input
                type="file"
                class="hidden"
                ref={props.fileInputRef}
                onChange={handleFileChange}
            />
        </>
    );
}