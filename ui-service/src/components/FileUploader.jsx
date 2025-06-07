import { useParams } from "@solidjs/router";
import { createSignal } from "solid-js";
import { apiRequest } from "../utils/apiRequest";


export default function FileUploader(props) {
    const [file, setFile] = createSignal();
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
        setFile(selectedFile);
        if (selectedFile) {
            uploadFile();
        }
    };

    return (
        <input
            type="file"
            class="hidden"
            ref={props.fileInputRef}
            onChange={handleFileChange}
        />
    );
}