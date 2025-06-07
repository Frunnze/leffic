import { useParams } from "@solidjs/router";
import { createEffect, createSignal } from "solid-js";
import { useNotificationContext } from "../context/NotificationContext";
import { apiRequest } from "../utils/apiRequest";
import GeneralDropdown from "./GeneralDropdown";
import FileUploader from "./FileUploader";
import LinkInput from "./LinkInput";
import TopicInput from "./TopicInput";


export default function AIImport(props) {
    const [flashcardsGenerationTaskId, setFlashcardsGenerationTaskId] = createSignal();
    const [noteGenerationTaskId, setNoteGenerationTaskId] = createSignal();
    const [testGenerationTaskId, setTestGenerationTaskId] = createSignal();
    const [dropdownState, setDropdownState] = createSignal(false);
    const [openLinkInput, setOpenLinkInput] = createSignal(false);
    const [openTopicInput, setOpenTopicInput] = createSignal(false);
    const {
        setDisplayStartGenerationNotification, 
        setFlashcardsTaskStatus,
        setNoteTaskStatus,
        setTestTaskStatus
    } = useNotificationContext();

    const params = useParams();

    async function generateStudyUnits(body) {
        const flashcardsGenerationResponse = await apiRequest({
            endpoint: "/api/files/generate-study-units",
            method: "POST",
            body: body
        })
        const studyUnitsGenerationResponseData = await flashcardsGenerationResponse.json()
        setFlashcardsGenerationTaskId(studyUnitsGenerationResponseData.task_id)
        setNoteGenerationTaskId(studyUnitsGenerationResponseData.note_task_id)
        setTestGenerationTaskId(studyUnitsGenerationResponseData.test_task_id)
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
            
            if (data.status === "SUCCESS") {
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
            clearInterval(interval);
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
                
                if (data.status === "SUCCESS") {
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
                clearInterval(interval);
            }
        }, 2000);        
        return () => clearInterval(interval);
        });

    // Check the test generation task
    createEffect(() => {
        if (!testGenerationTaskId()) return;
        const interval = setInterval(async () => {
            try {
                const res = await apiRequest({
                    endpoint: `/api/files/test-task-status/${testGenerationTaskId()}`
                })
                const data = await res.json();
                setTestTaskStatus(data.status)
                console.log("TEST GENERATION TASK STATUS", data)
                
                if (data.status === "SUCCESS") {
                    props.displayUnits([{
                        id: data.test_id,
                        name: data.name,
                        type: data.type,
                        created_at: data.created_at
                    }]);
                }
                if (data.status === "SUCCESS" || data.status === "FAILURE") {
                    clearInterval(interval); // stop polling
                    setTestGenerationTaskId(null);
                }
            } catch (err) {
                console.error("Error polling task status:", err);
                clearInterval(interval);
            }
        }, 2000);        
        return () => clearInterval(interval);
        });

    const fileSvg = (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
        <path d="M3.375 18C2.85937 18 2.41797 17.8238 2.05078 17.4713C1.68359 17.1188 1.5 16.695 1.5 16.2V1.8C1.5 1.305 1.68359 0.88125 2.05078 0.52875C2.41797 0.17625 2.85937 0 3.375 0H10.875L16.5 5.4V16.2C16.5 16.695 16.3164 17.1188 15.9492 17.4713C15.582 17.8238 15.1406 18 14.625 18H3.375ZM9.9375 6.3V1.8H3.375V16.2H14.625V6.3H9.9375Z" fill="#39393A"/>
        </svg>
    )
    const linkSvg = (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
        <g clip-path="url(#clip0_224_4)">
        <path d="M11.3753 2.55744C11.9148 2.01757 12.6466 1.71428 13.4097 1.71428C14.1727 1.71428 14.9045 2.01757 15.444 2.55744C15.9836 3.0973 16.2867 3.82952 16.2867 4.593C16.2867 5.35648 15.9836 6.08869 15.444 6.62856L14.0345 8.03779C13.8773 8.20072 13.7905 8.41889 13.7925 8.64529C13.7946 8.8717 13.8855 9.08824 14.0455 9.24826C14.2056 9.40829 14.4221 9.499 14.6484 9.50086C14.8747 9.50272 15.0926 9.41558 15.2553 9.25821L16.6637 7.84897C17.5021 6.9804 17.966 5.81708 17.9555 4.60957C17.9451 3.40207 17.461 2.24699 16.6076 1.39312C15.7543 0.539256 14.5999 0.0549175 13.3931 0.0444246C12.1863 0.0339317 11.0237 0.498124 10.1556 1.33702L6.70365 4.79103C6.25529 5.23969 5.90442 5.77622 5.67304 6.36695C5.44167 6.95769 5.33479 7.58988 5.3591 8.2239C5.3834 8.85791 5.53838 9.48006 5.8143 10.0513C6.09023 10.6226 6.48115 11.1306 6.96254 11.5436C7.13666 11.6891 7.361 11.7601 7.58705 11.7413C7.81309 11.7225 8.02265 11.6154 8.1704 11.4432C8.31815 11.271 8.39221 11.0475 8.37655 10.8211C8.36089 10.5947 8.25678 10.3836 8.08673 10.2334C7.7855 9.97538 7.54084 9.65785 7.36809 9.30072C7.19535 8.9436 7.09826 8.5546 7.08291 8.15814C7.06757 7.76169 7.13431 7.36634 7.27893 6.99692C7.42356 6.6275 7.64295 6.29198 7.92334 6.01144L11.3753 2.55744Z" fill="#39393A"/>
        <path d="M10.9632 6.54296C10.7906 6.3989 10.5682 6.32857 10.3442 6.34717C10.1202 6.36578 9.91248 6.47183 9.76604 6.64238C9.61961 6.81293 9.54621 7.03426 9.56173 7.25851C9.57725 7.48275 9.68044 7.69187 9.84897 7.84063C10.1475 8.09616 10.39 8.41065 10.5612 8.76435C10.7324 9.11805 10.8286 9.50333 10.8439 9.89599C10.8591 10.2886 10.7929 10.6802 10.6496 11.0461C10.5062 11.412 10.2888 11.7443 10.0109 12.0221L6.58966 15.443C6.05492 15.9777 5.32965 16.2781 4.57341 16.2781C3.81716 16.2781 3.09189 15.9777 2.55715 15.443C2.02241 14.9083 1.72199 14.1831 1.72199 13.427C1.72199 12.6708 2.02241 11.9456 2.55715 11.4109L3.95416 10.0152C4.10989 9.85382 4.196 9.63774 4.19394 9.4135C4.19189 9.18926 4.10184 8.9748 3.94318 8.81631C3.78452 8.65782 3.56996 8.56798 3.34569 8.56614C3.12143 8.56429 2.90542 8.6506 2.74418 8.80646L1.34831 10.2022C0.912625 10.623 0.565108 11.1263 0.326035 11.6827C0.0869632 12.2392 -0.038876 12.8378 -0.0441393 13.4434C-0.0494026 14.049 0.0660152 14.6496 0.29538 15.2102C0.524744 15.7708 0.863462 16.28 1.29177 16.7083C1.72008 17.1366 2.22939 17.4752 2.79001 17.7046C3.35062 17.9339 3.95129 18.0493 4.55699 18.0441C5.16268 18.0388 5.76126 17.913 6.31781 17.6739C6.87435 17.4349 7.3777 17.0874 7.7985 16.6518L11.2197 13.2308C11.6641 12.7865 12.0119 12.2551 12.2412 11.67C12.4705 11.0849 12.5764 10.4588 12.5523 9.83086C12.5282 9.20292 12.3746 8.58674 12.1012 8.02095C11.8277 7.45516 11.4403 6.95198 10.9632 6.54296Z" fill="#39393A"/>
        </g>
        <defs>
        <clipPath id="clip0_224_4">
        <rect width="18" height="18" fill="white"/>
        </clipPath>
        </defs>
        </svg>
    )
    const topicSvg = (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
        <g clip-path="url(#clip0_224_9)">
        <path d="M0 8.4L4.55336 0L9.10672 8.4H0ZM4.55336 18C3.60474 18 2.79842 17.648 2.13439 16.944C1.47036 16.24 1.13834 15.3937 1.13834 14.4052C1.13834 13.4017 1.47036 12.55 2.13439 11.85C2.79842 11.15 3.60474 10.8 4.55336 10.8C5.50198 10.8 6.3083 11.15 6.97233 11.85C7.63636 12.55 7.96838 13.4 7.96838 14.4C7.96838 15.4 7.63636 16.25 6.97233 16.95C6.3083 17.65 5.50198 18 4.55336 18ZM4.55834 16.2C5.02933 16.2 5.43083 16.0232 5.76285 15.6697C6.09486 15.3162 6.26087 14.8913 6.26087 14.3948C6.26087 13.8983 6.0932 13.475 5.75787 13.125C5.42253 12.775 5.01937 12.6 4.54838 12.6C4.07739 12.6 3.67589 12.7767 3.34387 13.1302C3.01186 13.4837 2.84585 13.9087 2.84585 14.4052C2.84585 14.9017 3.01352 15.325 3.34885 15.675C3.68419 16.025 4.08735 16.2 4.55834 16.2ZM2.96443 6.6H6.14229L4.55336 3.625L2.96443 6.6ZM10.2451 18V10.8H17.0751V18H10.2451ZM11.9526 16.2H15.3676V12.6H11.9526V16.2ZM13.6601 8.4C12.8063 7.65 12.1023 7.02842 11.548 6.53525C10.9938 6.04225 10.5511 5.60892 10.2199 5.23525C9.88885 4.86175 9.65613 4.51667 9.52174 4.2C9.38735 3.88333 9.32016 3.52775 9.32016 3.13325C9.32016 2.42292 9.5415 1.82317 9.98419 1.334C10.4269 0.844666 10.9997 0.6 11.7026 0.6C12.1064 0.6 12.4704 0.6875 12.7945 0.8625C13.1186 1.0375 13.4071 1.30833 13.6601 1.675C13.913 1.30833 14.2055 1.0375 14.5375 0.8625C14.8696 0.6875 15.2346 0.6 15.6327 0.6C16.3255 0.6 16.8933 0.844666 17.336 1.334C17.7787 1.82317 18 2.42292 18 3.13325C18 3.52775 17.9368 3.88333 17.8103 4.2C17.6838 4.51667 17.4535 4.86 17.1194 5.23C16.7854 5.6 16.3387 6.02917 15.7795 6.5175C15.2203 7.00583 14.5138 7.63333 13.6601 8.4ZM13.6601 6C14.7352 5.05 15.4427 4.39583 15.7826 4.0375C16.1225 3.67917 16.2925 3.36667 16.2925 3.1C16.2925 2.91667 16.2292 2.75417 16.1028 2.6125C15.9763 2.47083 15.8281 2.4 15.6583 2.4C15.5277 2.4 15.4071 2.43333 15.2964 2.5C15.1858 2.56667 15.0909 2.65 15.0119 2.75L13.6601 4.075L12.332 2.75C12.2372 2.65 12.1327 2.56667 12.0187 2.5C11.9049 2.43333 11.788 2.4 11.668 2.4C11.4941 2.4 11.3439 2.47083 11.2174 2.6125C11.0909 2.75417 11.0277 2.91667 11.0277 3.1C11.0277 3.38333 11.2055 3.70833 11.5613 4.075C11.917 4.44167 12.6166 5.08333 13.6601 6Z" fill="#39393A"/>
        </g>
        <defs>
        <clipPath id="clip0_224_9">
        <rect width="18" height="18" fill="white"/>
        </clipPath>
        </defs>
        </svg>
    )
    let fileInputRef;
    return (
        <>
            <button onClick={() => setDropdownState(!dropdownState())} class="relative btn-primary">
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
                <span>AI Import</span>
                <GeneralDropdown
                    dropdownState={dropdownState} setDropdownState={setDropdownState}
                    dropDownItems={[
                        {trigger: () => fileInputRef?.click(), label: "File", svg: fileSvg},
                        {trigger: () => setOpenLinkInput(true), label: "Link", svg: linkSvg},
                        {trigger: () => setOpenTopicInput(true), label: "Topic", svg: topicSvg},
                    ]}
                    position="top-10 left-0"
                />
            </button>

            <FileUploader 
                fileInputRef={el => fileInputRef = el} 
                generateStudyUnits={generateStudyUnits}
                displayUnits={props.displayUnits}
            />

            <Show when={openLinkInput()}>
                <LinkInput
                    generateStudyUnits={generateStudyUnits}
                    setOpenLinkInput={setOpenLinkInput}
                />
            </Show>

            <Show when={openTopicInput()}>
                <TopicInput
                    generateStudyUnits={generateStudyUnits}
                    setOpenTopicInput={setOpenTopicInput}
                />
            </Show>
        </>
    );
}