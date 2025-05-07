import { createResource, Show } from "solid-js";
import LeftNavBar from "../components/LeftNavBar";
import { useParams } from "@solidjs/router";
import { apiRequest } from "../utils/apiRequest";


const getNote = async (noteId) => {
    const res = await apiRequest({
        endpoint: `/api/content/note?${new URLSearchParams({
            note_id: noteId
        }).toString()}`,
    });
    const data = await res.json();
    console.log(data);
    return data;
};


export default function NotesReview() {
    const params = useParams();
    const [note] = createResource(
        () => params.id,
        getNote
    );

    return (
        <div class="h-full flex justify-center text-tertiary-100 bg-secondary/10 pl-17">
            <LeftNavBar/>
            <Show when={note()}>
                <div class="bg-primary w-[90%] md:w-[55%] shadow p-5 border border-tertiary-10 rounded-md h-full border my-15 flex flex-col text-tertiary-100">
                    <span class="font-semibold text-xl">
                        {note().name}
                    </span>
                    <br/>
                    <hr class="border-0.1 border-tertiary-10"/>
                    <br/>
                    <div class="h-full prose prose-headings:text-lg prose-headings:text-tertiary-100 prose-p:text-tertiary-100" innerHTML={note().content}/>
                </div>
            </Show>
        </div>
    );
}