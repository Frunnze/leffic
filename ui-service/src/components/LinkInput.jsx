import { useParams } from "@solidjs/router";
import { createSignal } from "solid-js";
import { apiRequest } from "../utils/apiRequest";


export default function LinkInput(props) {
    const params = useParams();
    const [link, setLink] = createSignal("");

    return (
        <div class="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm bg-tertiary-100/10">
            <div class="bg-primary p-6 rounded-2xl shadow-2xl w-full max-w-md">
                <h2 class="text-xl font-semibold mb-4">Generate study units</h2>
                <input
                    type="text"
                    value={link()}
                    onInput={(e) => setLink(e.currentTarget.value)}
                    placeholder="Link"
                    class="w-full p-2 border border-tertiary-40 rounded-lg mb-4"
                />
                <div class="flex justify-end gap-2">
                <button
                    class="border border-tertiary-40 text-tertiary-100 px-4 py-2 bg-primary rounded-lg hover:bg-tertiary-2 cursor-pointer"
                    onClick={() => props.setOpenLinkInput(false)}
                >
                    Cancel
                </button>
                <button onClick={async () => {
                        await props.generateStudyUnits(
                            {
                                note: {},
                                test: {},
                                flashcards: {},
                                folder_id: params.id,
                                link_metadata: link()
                            }
                        );
                        props.setOpenLinkInput(false);
                    }}
                    class="px-4 py-2 bg-secondary text-primary rounded-lg hover:bg-secondary/90 cursor-pointer">
                    Generate
                </button>
                </div>
            </div>
        </div>
    );
}