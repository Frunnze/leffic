import { useParams } from "@solidjs/router";
import { createSignal } from "solid-js";

export default function NewFolder(props) {
    const params = useParams();
    const [open, setOpen] = createSignal(false);
    const [folderName, setFolderName] = createSignal("");

    const createNewFolder = async () => {
        console.log(folderName())
        const res = await fetch("http://localhost:8888/api/content/create-folder", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "user_id": "23da4be0-70fd-439b-b984-aaf729959e9a",
                "parent_folder_id": params.id,
                "folder_name": folderName()
            })
        })
        const resData = await res.json()
        props.displayUnits([{
            id: resData.folder_id,
            name: resData.folder_name,
            createdAt: resData.created_at,
            type: "folder",
        }])
        setOpen(false);
    }

    return (
        <>
            <button onClick={() => setOpen(true)} class="btn-primary">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <path d="M10.8 12.78H12.6V10.89H14.4V9H12.6V7.11H10.8V9H9V10.89H10.8V12.78ZM1.8 16.56C1.305 16.56 0.88125 16.3749 0.52875 16.0048C0.17625 15.6347 0 15.1897 0 14.67V3.33C0 2.81025 0.17625 2.36531 0.52875 1.99519C0.88125 1.62506 1.305 1.44 1.8 1.44H7.2L9 3.33H16.2C16.695 3.33 17.1188 3.51506 17.4713 3.88519C17.8238 4.25531 18 4.70025 18 5.22V14.67C18 15.1897 17.8238 15.6347 17.4713 16.0048C17.1188 16.3749 16.695 16.56 16.2 16.56H1.8ZM1.8 14.67H16.2V5.22H8.2575L6.4575 3.33H1.8V14.67Z" fill="#39393A"/>
                </svg>
                <span>New folder</span>
            </button>
            <Show when={open()}>
                <div class="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm bg-tertiary-100/10">
                    <div class="bg-primary p-6 rounded-2xl shadow-2xl w-full max-w-md">
                        <h2 class="text-xl font-semibold mb-4">Create New Folder</h2>
                        <input
                            type="text"
                            value={folderName()}
                            onInput={(e) => setFolderName(e.currentTarget.value)}
                            placeholder="Folder name"
                            class="w-full p-2 border border-tertiary-40 rounded-lg mb-4"
                        />
                        <div class="flex justify-end gap-2">
                        <button
                            class="border border-tertiary-40 text-tertiary-100 px-4 py-2 bg-primary rounded-lg hover:bg-tertiary-2 cursor-pointer"
                            onClick={() => setOpen(false)}
                        >
                            Cancel
                        </button>
                        <button onClick={createNewFolder} class="px-4 py-2 bg-secondary text-primary rounded-lg hover:bg-secondary/90 cursor-pointer">
                            Create
                        </button>
                        </div>
                    </div>
                </div>
            </Show>
        </>
    );
}
