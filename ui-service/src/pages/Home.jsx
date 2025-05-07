import { createResource, createSignal, createEffect, Switch, Match, onCleanup, Show } from "solid-js";
import { A, useParams } from "@solidjs/router";
import LeftNavBar from "../components/LeftNavBar";
import FileUploader from "../components/FileUploader";
import NewFolder from "../components/NewFolder";
import FlashcardsMixedReview from "../components/FlashcardsMixedReview";
import { apiRequest } from "../utils/apiRequest";
import { useNavigate } from '@solidjs/router';
// import { setRedirectToLogin } from "../utils/apiRequest"


function sortUnitsByCreatedTime(units) {
    return units.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
}

const getFolders = async (folderId) => {
    const res = await apiRequest({
        endpoint: `/api/content/access-folder/?${new URLSearchParams({ 
            folder_id: folderId 
        }).toString()}`,
    });
    let data = await res.json();
    console.log("/api/content/access-folder", data);
    data = {
        content: sortUnitsByCreatedTime(data["content"]),
        parent_folder_name: data.parent_folder_name
    }
    return data;
};

export default function Home() {    
    const params = useParams();
    const [folderContent, {mutate: mutateFolderContent, refetch}] = createResource(
        () => params.id,
        getFolders
    );
    const [flashcardsReview, setFlashcardsReview] = createSignal(false);
    const [unitIdSignal, setUnitIdSignal] = createSignal();

    const [unitDropdownState, setUnitDropdownState] = createSignal(null);
    const [dropdownState, setDropdownState] = createSignal(false);
    const deleteUnit = async (unitId, unitType) => {
        if (unitType == "folder") {
            await apiRequest({
                endpoint: `/api/content/delete-folder/?folder_id=${unitId}`,
                method: "DELETE"
            })
            const updatedContent = {
                content: folderContent().content.filter(unit => unit.id !== unitId),
                parent_folder_name: folderContent().parent_folder_name
            }
            mutateFolderContent(updatedContent);
            setUnitDropdownState(null);
        };
    }

    function displayUnits(newUnits) {
        const updatedContent = {
            content: sortUnitsByCreatedTime([
              ...newUnits,
              ...folderContent().content,
            ]),
            parent_folder_name: folderContent().parent_folder_name
        };
        console.log("updatedContent", updatedContent);
        mutateFolderContent(updatedContent);
    }

    function unitDropdownOptions(e, unitId) {
        e.preventDefault();
        e.stopPropagation();
        if (unitDropdownState()) {
            setUnitDropdownState(null);
        } else {
            setUnitDropdownState(unitId);
        }
    }

    function openFlashcardsReview(unitId) {
        setUnitIdSignal(unitId);
        setFlashcardsReview(true);
    }

    // Click outside handler
    const [dropdownRef, setDropdownRef] = createSignal(null);
    createEffect(() => {
        if (unitDropdownState() || dropdownState()) {
            const handleClickOutside = (e) => {
                if (dropdownRef() && !dropdownRef().contains(e.target)) {
                    setUnitDropdownState(null);
                    setDropdownState(false);
                }
            };
            
            document.addEventListener("click", handleClickOutside);
            onCleanup(() => {
                document.removeEventListener("click", handleClickOutside);
            });
        }
    });

    return (
        <>
        <Show when={flashcardsReview()}>
            <FlashcardsMixedReview setFlashcardsReview={setFlashcardsReview} folderId={unitIdSignal()} />
        </Show>
        <div class="pl-17 relative flex text-tertiary-100 h-full">
            <LeftNavBar/>
            <div class="flex flex-col w-full h-full py-17 px-10 md:px-40 lg:px-80 gap-y-4">
                <div class="flex items-center w-full mb-4">
                    <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="30" height="23" viewBox="0 0 27 20" fill="none">
                        <g clip-path="url(#clip0_9_17)">
                        <path d="M2.51163 20.2597C1.82093 20.2597 1.22965 20.0118 0.737791 19.5158C0.24593 19.0199 0 18.4237 0 17.7273V2.53247C0 1.83604 0.24593 1.23985 0.737791 0.743912C1.22965 0.247971 1.82093 0 2.51163 0H10.0465L12.5581 2.53247H22.6047C23.2953 2.53247 23.8866 2.78044 24.3785 3.27638C24.8703 3.77232 25.1163 4.36851 25.1163 5.06494H11.5221L9.01046 2.53247H2.51163V17.7273L5.52558 7.5974H27L23.7663 18.4554C23.5988 19.0041 23.2901 19.442 22.8401 19.7691C22.3901 20.0962 21.893 20.2597 21.3488 20.2597H2.51163ZM5.14884 17.7273H21.3488L23.6093 10.1299H7.4093L5.14884 17.7273Z" fill="#3083DC"/>
                        <path d="M5.14884 17.7273H21.3488L23.6093 10.1299H7.4093L5.14884 17.7273Z" fill="#3083DC"/>
                        </g>
                        <defs>
                        <clipPath id="clip0_9_17">
                        <rect width="27" height="20" fill="white"/>
                        </clipPath>
                        </defs>
                    </svg>
                    <Show when={!folderContent.loading}>
                        <span class="text-2xl font-semibold pl-2 truncate">
                            {folderContent().parent_folder_name}
                        </span>
                    </Show>
                </div>

                <div class="flex justify-between gap-4 flex-wrap">
                    <div class="flex gap-x-4 flex-wrap gap-4">
                        <div onClick={() => setDropdownState(true)} class="relative bg-secondary text-primary flex items-center gap-2 py-1.5 px-3 rounded-md cursor-pointer font-medium text-sm md:text-base text-nowrap">
                            <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                                <path d="M8.99997 18C8.00866 17.0512 6.87279 16.3256 5.59236 15.8233C4.31192 15.3209 2.96953 15.0698 1.56519 15.0698V5.86047C2.95577 5.86047 4.29127 6.11512 5.57171 6.62442C6.85214 7.13372 7.9949 7.86977 8.99997 8.83256C10.005 7.86977 11.1478 7.13372 12.4282 6.62442C13.7087 6.11512 15.0442 5.86047 16.4348 5.86047V15.0698C15.0166 15.0698 13.6708 15.3209 12.3973 15.8233C11.1237 16.3256 9.99127 17.0512 8.99997 18ZM8.99997 15.8233C9.86736 15.1674 10.7898 14.6442 11.7674 14.2535C12.7449 13.8628 13.75 13.6047 14.7826 13.4791V7.70233C13.7775 7.88372 12.7896 8.25 11.819 8.80116C10.8483 9.35233 9.90866 10.0884 8.99997 11.0093C8.09127 10.0884 7.1516 9.35233 6.18095 8.80116C5.21029 8.25 4.22243 7.88372 3.21736 7.70233V13.4791C4.24997 13.6047 5.25504 13.8628 6.23258 14.2535C7.21011 14.6442 8.13258 15.1674 8.99997 15.8233ZM8.99997 6.69767C8.09127 6.69767 7.31337 6.36977 6.66627 5.71395C6.01917 5.05814 5.69562 4.26977 5.69562 3.34884C5.69562 2.42791 6.01917 1.63953 6.66627 0.983721C7.31337 0.327907 8.09127 0 8.99997 0C9.90866 0 10.6866 0.327907 11.3337 0.983721C11.9808 1.63953 12.3043 2.42791 12.3043 3.34884C12.3043 4.26977 11.9808 5.05814 11.3337 5.71395C10.6866 6.36977 9.90866 6.69767 8.99997 6.69767ZM8.99997 5.02326C9.45432 5.02326 9.84327 4.8593 10.1668 4.5314C10.4904 4.20349 10.6521 3.8093 10.6521 3.34884C10.6521 2.88837 10.4904 2.49419 10.1668 2.16628C9.84327 1.83837 9.45432 1.67442 8.99997 1.67442C8.54562 1.67442 8.15667 1.83837 7.83312 2.16628C7.50957 2.49419 7.34779 2.88837 7.34779 3.34884C7.34779 3.8093 7.50957 4.20349 7.83312 4.5314C8.15667 4.8593 8.54562 5.02326 8.99997 5.02326Z" fill="white"/>
                            </svg>
                            <span>Study</span>
                            <Show when={dropdownState()}>
                                <div ref={setDropdownRef} class="text-tertiary-100 absolute top-10 left-0 font-medium border border-tertiary-10 bg-primary flex flex-col justify-content items-center text-sm z-50 mt-2 w-56 origin-top-right rounded-md shadow-lg">
                                    <div onClick={() => openFlashcardsReview(params.id)} class="rounded-tl-md rounded-tr-md flex gap-2 items-center cursor-pointer hover:bg-tertiary-2  w-full h-full border-b border-tertiary-10 p-3">
                                        <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 20 20">
                                            <g clip-path="url(#clip0_125_7)">
                                            <path d="M10.6921 17.0382H16.3226C16.2053 17.4737 16.0042 17.8255 15.7193 18.0935C15.4344 18.3615 15.0658 18.529 14.6133 18.596L3.65395 19.9277C3.10096 20.0115 2.60242 19.8817 2.15835 19.5383C1.71428 19.1949 1.45873 18.7468 1.3917 18.194L0.059482 7.21385C-0.0075477 6.66107 0.126512 6.16692 0.461661 5.7314C0.796809 5.29588 1.24088 5.04461 1.79388 4.97761L2.95014 4.82685V6.83695L2.04524 6.96259L3.40259 17.9428L10.6921 17.0382ZM6.97192 15.0281C6.41893 15.0281 5.94553 14.8313 5.55173 14.4376C5.15793 14.044 4.96103 13.5708 4.96103 13.018V1.96246C4.96103 1.40968 5.15793 0.936473 5.55173 0.542829C5.94553 0.149184 6.41893 -0.0476379 6.97192 -0.0476379H18.0318C18.5848 -0.0476379 19.0582 0.149184 19.452 0.542829C19.8458 0.936473 20.0427 1.40968 20.0427 1.96246V13.018C20.0427 13.5708 19.8458 14.044 19.452 14.4376C19.0582 14.8313 18.5848 15.0281 18.0318 15.0281H6.97192ZM6.97192 13.018H18.0318V1.96246H6.97192V13.018Z"/>
                                            <path d="M13.3908 3.24116C13.4092 3.16418 13.3986 3.08393 13.3604 3.01289C13.3223 2.94184 13.2589 2.88399 13.1799 2.84831C13.101 2.81263 13.011 2.80113 12.924 2.81559C12.8369 2.83005 12.7577 2.86967 12.6986 2.92829L8.14504 7.45239C8.09333 7.50378 8.05946 7.56738 8.04752 7.6355C8.03557 7.70363 8.04607 7.77337 8.07773 7.83631C8.10939 7.89925 8.16087 7.9527 8.22596 7.9902C8.29104 8.02771 8.36694 8.04766 8.4445 8.04767H11.9652L11.2661 10.9493C11.2476 11.0263 11.2583 11.1065 11.2964 11.1776C11.3346 11.2486 11.398 11.3065 11.4769 11.3421C11.5559 11.3778 11.6459 11.3893 11.7329 11.3749C11.8199 11.3604 11.8992 11.3208 11.9583 11.2622L16.5118 6.73806C16.5635 6.68667 16.5974 6.62307 16.6094 6.55495C16.6213 6.48682 16.6108 6.41708 16.5791 6.35414C16.5475 6.2912 16.496 6.23775 16.4309 6.20024C16.3658 6.16274 16.2899 6.14278 16.2124 6.14278H12.6917L13.3908 3.24116Z"/>
                                            </g>
                                            <defs>
                                            <clipPath id="clip0_125_7">
                                            <rect width="20" height="20" fill="white"/>
                                            </clipPath>
                                            </defs>
                                        </svg>
                                        Flashcards
                                    </div>
                                    <div class="rounded-bl-md rounded-br-md flex gap-2 items-center cursor-pointer hover:bg-tertiary-2  w-full h-full p-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                                            <g clip-path="url(#clip0_166_8)">
                                            <path d="M10.8 11.7C11.055 11.7 11.2763 11.6063 11.4638 11.4188C11.6513 11.2313 11.745 11.01 11.745 10.755C11.745 10.5 11.6513 10.2788 11.4638 10.0913C11.2763 9.90375 11.055 9.81 10.8 9.81C10.545 9.81 10.3238 9.90375 10.1363 10.0913C9.94875 10.2788 9.855 10.5 9.855 10.755C9.855 11.01 9.94875 11.2313 10.1363 11.4188C10.3238 11.6063 10.545 11.7 10.8 11.7ZM10.125 8.82H11.475C11.475 8.385 11.52 8.06625 11.61 7.86375C11.7 7.66125 11.91 7.395 12.24 7.065C12.69 6.615 12.99 6.25125 13.14 5.97375C13.29 5.69625 13.365 5.37 13.365 4.995C13.365 4.32 13.1288 3.76875 12.6563 3.34125C12.1838 2.91375 11.565 2.7 10.8 2.7C10.185 2.7 9.64875 2.8725 9.19125 3.2175C8.73375 3.5625 8.415 4.02 8.235 4.59L9.45 5.085C9.585 4.71 9.76875 4.42875 10.0013 4.24125C10.2338 4.05375 10.5 3.96 10.8 3.96C11.16 3.96 11.4525 4.06125 11.6775 4.26375C11.9025 4.46625 12.015 4.74 12.015 5.085C12.015 5.295 11.955 5.49375 11.835 5.68125C11.715 5.86875 11.505 6.105 11.205 6.39C10.71 6.825 10.4063 7.16625 10.2938 7.41375C10.1813 7.66125 10.125 8.13 10.125 8.82ZM5.4 14.4C4.905 14.4 4.48125 14.2238 4.12875 13.8713C3.77625 13.5188 3.6 13.095 3.6 12.6V1.8C3.6 1.305 3.77625 0.88125 4.12875 0.52875C4.48125 0.17625 4.905 0 5.4 0H16.2C16.695 0 17.1188 0.17625 17.4713 0.52875C17.8238 0.88125 18 1.305 18 1.8V12.6C18 13.095 17.8238 13.5188 17.4713 13.8713C17.1188 14.2238 16.695 14.4 16.2 14.4H5.4ZM5.4 12.6H16.2V1.8H5.4V12.6ZM1.8 18C1.305 18 0.88125 17.8238 0.52875 17.4713C0.17625 17.1188 0 16.695 0 16.2V3.6H1.8V16.2H14.4V18H1.8Z" fill="#39393A"/>
                                            </g>
                                            <defs>
                                            <clipPath id="clip0_166_8">
                                            <rect width="18" height="18" fill="white"/>
                                            </clipPath>
                                            </defs>
                                        </svg>
                                        Tests
                                    </div>
                                </div>
                            </Show>
                        </div>

                        <FileUploader displayUnits={displayUnits}/>
                        <NewFolder displayUnits={displayUnits}/>
                        {/* <button class="btn-primary">
                            <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                                <path d="M7.73437 14.4H9.51562V11.7H12.1875V9.9H9.51562V7.2H7.73437V9.9H5.0625V11.7H7.73437V14.4ZM3.28125 18C2.79141 18 2.37207 17.8238 2.02324 17.4713C1.67441 17.1188 1.5 16.695 1.5 16.2V1.8C1.5 1.305 1.67441 0.88125 2.02324 0.52875C2.37207 0.17625 2.79141 0 3.28125 0H10.4062L15.75 5.4V16.2C15.75 16.695 15.5756 17.1188 15.2268 17.4713C14.8779 17.8238 14.4586 18 13.9687 18H3.28125ZM9.51562 6.3V1.8H3.28125V16.2H13.9687V6.3H9.51562Z" fill="#39393A"/>
                            </svg>
                            <span>New file</span>
                        </button> */}
                    </div>
                <button class="btn-primary">
                    <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                        <path d="M2.25 11.25C1.63125 11.25 1.10156 11.0297 0.660937 10.5891C0.220312 10.1484 0 9.61875 0 9C0 8.38125 0.220312 7.85156 0.660937 7.41094C1.10156 6.97031 1.63125 6.75 2.25 6.75C2.86875 6.75 3.39844 6.97031 3.83906 7.41094C4.27969 7.85156 4.5 8.38125 4.5 9C4.5 9.61875 4.27969 10.1484 3.83906 10.5891C3.39844 11.0297 2.86875 11.25 2.25 11.25ZM9 11.25C8.38125 11.25 7.85156 11.0297 7.41094 10.5891C6.97031 10.1484 6.75 9.61875 6.75 9C6.75 8.38125 6.97031 7.85156 7.41094 7.41094C7.85156 6.97031 8.38125 6.75 9 6.75C9.61875 6.75 10.1484 6.97031 10.5891 7.41094C11.0297 7.85156 11.25 8.38125 11.25 9C11.25 9.61875 11.0297 10.1484 10.5891 10.5891C10.1484 11.0297 9.61875 11.25 9 11.25ZM15.75 11.25C15.1312 11.25 14.6016 11.0297 14.1609 10.5891C13.7203 10.1484 13.5 9.61875 13.5 9C13.5 8.38125 13.7203 7.85156 14.1609 7.41094C14.6016 6.97031 15.1312 6.75 15.75 6.75C16.3687 6.75 16.8984 6.97031 17.3391 7.41094C17.7797 7.85156 18 8.38125 18 9C18 9.61875 17.7797 10.1484 17.3391 10.5891C16.8984 11.0297 16.3687 11.25 15.75 11.25Z" fill="#39393A"/>
                    </svg>
                </button>
                </div>

                <div class="relative flex flex-col gap-4">
                    <hr class="border-tertiary-10"/>
                    <Show when={folderContent() && folderContent().content.length == 0}>
                        <span class="absolute text-tertiary-40 top-50 left-1/2 -translate-x-1/2 -translate-y-1/2">
                            Empty folder
                        </span>
                    </Show>
                    <Show when={folderContent()} fallback={<p>Contents are loading...</p>}>
                        <For each={folderContent().content}>
                            {(unit) => (
                                <div class="relative">
                                    <A href={`/${unit.type}/` + unit.id} class="flex gap-2 items-center w-full justify-between py-1.5 px-3 border border-tertiary-40 rounded-md hover:bg-secondary hover:fill-primary hover:text-primary hover:border-transparent hover:shadow-sm cursor-pointer font-medium text-sm truncate">
                                        <div class="flex gap-2 w-[80%]">
                                            <Switch>
                                                <Match when={unit.type === "folder"}>
                                                    <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                                                        <path d="M2 17.6923C1.45 17.6923 0.979167 17.4946 0.5875 17.0992C0.195833 16.7037 0 16.2284 0 15.6731V3.55768C0 3.00239 0.195833 2.52703 0.5875 2.1316C0.979167 1.73617 1.45 1.53845 2 1.53845H8L10 3.55768H18C18.55 3.55768 19.0208 3.7554 19.4125 4.15083C19.8042 4.54626 20 5.02163 20 5.57691V15.6731C20 16.2284 19.8042 16.7037 19.4125 17.0992C19.0208 17.4946 18.55 17.6923 18 17.6923H2ZM2 15.6731H18V5.57691H9.175L7.175 3.55768H2V15.6731Z"/>
                                                    </svg>
                                                </Match>
                                                <Match when={unit.type === "flashcard_deck"}>
                                                    <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                                                        <g clip-path="url(#clip0_125_7)">
                                                        <path d="M10.6921 17.0382H16.3226C16.2053 17.4737 16.0042 17.8255 15.7193 18.0935C15.4344 18.3615 15.0658 18.529 14.6133 18.596L3.65395 19.9277C3.10096 20.0115 2.60242 19.8817 2.15835 19.5383C1.71428 19.1949 1.45873 18.7468 1.3917 18.194L0.059482 7.21385C-0.0075477 6.66107 0.126512 6.16692 0.461661 5.7314C0.796809 5.29588 1.24088 5.04461 1.79388 4.97761L2.95014 4.82685V6.83695L2.04524 6.96259L3.40259 17.9428L10.6921 17.0382ZM6.97192 15.0281C6.41893 15.0281 5.94553 14.8313 5.55173 14.4376C5.15793 14.044 4.96103 13.5708 4.96103 13.018V1.96246C4.96103 1.40968 5.15793 0.936473 5.55173 0.542829C5.94553 0.149184 6.41893 -0.0476379 6.97192 -0.0476379H18.0318C18.5848 -0.0476379 19.0582 0.149184 19.452 0.542829C19.8458 0.936473 20.0427 1.40968 20.0427 1.96246V13.018C20.0427 13.5708 19.8458 14.044 19.452 14.4376C19.0582 14.8313 18.5848 15.0281 18.0318 15.0281H6.97192ZM6.97192 13.018H18.0318V1.96246H6.97192V13.018Z"/>
                                                        <path d="M13.3908 3.24116C13.4092 3.16418 13.3986 3.08393 13.3604 3.01289C13.3223 2.94184 13.2589 2.88399 13.1799 2.84831C13.101 2.81263 13.011 2.80113 12.924 2.81559C12.8369 2.83005 12.7577 2.86967 12.6986 2.92829L8.14504 7.45239C8.09333 7.50378 8.05946 7.56738 8.04752 7.6355C8.03557 7.70363 8.04607 7.77337 8.07773 7.83631C8.10939 7.89925 8.16087 7.9527 8.22596 7.9902C8.29104 8.02771 8.36694 8.04766 8.4445 8.04767H11.9652L11.2661 10.9493C11.2476 11.0263 11.2583 11.1065 11.2964 11.1776C11.3346 11.2486 11.398 11.3065 11.4769 11.3421C11.5559 11.3778 11.6459 11.3893 11.7329 11.3749C11.8199 11.3604 11.8992 11.3208 11.9583 11.2622L16.5118 6.73806C16.5635 6.68667 16.5974 6.62307 16.6094 6.55495C16.6213 6.48682 16.6108 6.41708 16.5791 6.35414C16.5475 6.2912 16.496 6.23775 16.4309 6.20024C16.3658 6.16274 16.2899 6.14278 16.2124 6.14278H12.6917L13.3908 3.24116Z"/>
                                                        </g>
                                                        <defs>
                                                        <clipPath id="clip0_125_7">
                                                        <rect width="20" height="20" fill="white"/>
                                                        </clipPath>
                                                        </defs>
                                                    </svg>
                                                </Match>
                                                <Match when={unit.type === "file"}>
                                                    <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                                                        <path d="M3.74996 20C3.17704 20 2.68659 19.8042 2.27861 19.4125C1.87062 19.0208 1.66663 18.55 1.66663 18V2C1.66663 1.45 1.87062 0.979167 2.27861 0.5875C2.68659 0.195833 3.17704 0 3.74996 0H12.0833L18.3333 6V18C18.3333 18.55 18.1293 19.0208 17.7213 19.4125C17.3133 19.8042 16.8229 20 16.25 20H3.74996ZM11.0416 7V2H3.74996V18H16.25V7H11.0416Z"/>
                                                    </svg>
                                                </Match>
                                                <Match when={unit.type === "note"}>
                                                    <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                                                        <path d="M6.45833 16H14.375V14H6.45833V16ZM6.45833 12H14.375V10H6.45833V12ZM4.47917 20C3.9349 20 3.46897 19.8042 3.08138 19.4125C2.69379 19.0208 2.5 18.55 2.5 18V2C2.5 1.45 2.69379 0.979167 3.08138 0.5875C3.46897 0.195833 3.9349 0 4.47917 0H12.3958L18.3333 6V18C18.3333 18.55 18.1395 19.0208 17.752 19.4125C17.3644 19.8042 16.8984 20 16.3542 20H4.47917ZM11.4062 7V2H4.47917V18H16.3542V7H11.4062Z"/>
                                                    </svg>
                                                </Match>
                                            </Switch>
                                            <span class="truncate">{unit.name}</span>
                                        </div>
                                        <button 
                                            onClick={(e) => unitDropdownOptions(e, unit.id)}
                                            class="cursor-pointer rounded-sm px-1 hover:bg-tertiary-30">
                                            <svg class="fill-inherit flex-none" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                                                <path d="M2.25 11.25C1.63125 11.25 1.10156 11.0297 0.660937 10.5891C0.220312 10.1484 0 9.61875 0 9C0 8.38125 0.220312 7.85156 0.660937 7.41094C1.10156 6.97031 1.63125 6.75 2.25 6.75C2.86875 6.75 3.39844 6.97031 3.83906 7.41094C4.27969 7.85156 4.5 8.38125 4.5 9C4.5 9.61875 4.27969 10.1484 3.83906 10.5891C3.39844 11.0297 2.86875 11.25 2.25 11.25ZM9 11.25C8.38125 11.25 7.85156 11.0297 7.41094 10.5891C6.97031 10.1484 6.75 9.61875 6.75 9C6.75 8.38125 6.97031 7.85156 7.41094 7.41094C7.85156 6.97031 8.38125 6.75 9 6.75C9.61875 6.75 10.1484 6.97031 10.5891 7.41094C11.0297 7.85156 11.25 8.38125 11.25 9C11.25 9.61875 11.0297 10.1484 10.5891 10.5891C10.1484 11.0297 9.61875 11.25 9 11.25ZM15.75 11.25C15.1312 11.25 14.6016 11.0297 14.1609 10.5891C13.7203 10.1484 13.5 9.61875 13.5 9C13.5 8.38125 13.7203 7.85156 14.1609 7.41094C14.6016 6.97031 15.1312 6.75 15.75 6.75C16.3687 6.75 16.8984 6.97031 17.3391 7.41094C17.7797 7.85156 18 8.38125 18 9C18 9.61875 17.7797 10.1484 17.3391 10.5891C16.8984 11.0297 16.3687 11.25 15.75 11.25Z"/>
                                            </svg>
                                        </button>
                                    </A>
                                    <Show when={unitDropdownState() == unit.id}>
                                        <div ref={setDropdownRef} class="font-medium border border-tertiary-10 bg-primary flex flex-col justify-content items-center text-sm absolute z-50 right-0 mt-2 w-56 origin-top-right rounded-md shadow-lg">
                                            <Show when={unit.type === "folder"}>
                                                <div onClick={() => openFlashcardsReview(unit.id)} class="rounded-tl-md rounded-tr-md flex gap-2 items-center cursor-pointer hover:bg-tertiary-2  w-full h-full border-b border-tertiary-10 p-3">
                                                    <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 20 20">
                                                        <g clip-path="url(#clip0_125_7)">
                                                        <path d="M10.6921 17.0382H16.3226C16.2053 17.4737 16.0042 17.8255 15.7193 18.0935C15.4344 18.3615 15.0658 18.529 14.6133 18.596L3.65395 19.9277C3.10096 20.0115 2.60242 19.8817 2.15835 19.5383C1.71428 19.1949 1.45873 18.7468 1.3917 18.194L0.059482 7.21385C-0.0075477 6.66107 0.126512 6.16692 0.461661 5.7314C0.796809 5.29588 1.24088 5.04461 1.79388 4.97761L2.95014 4.82685V6.83695L2.04524 6.96259L3.40259 17.9428L10.6921 17.0382ZM6.97192 15.0281C6.41893 15.0281 5.94553 14.8313 5.55173 14.4376C5.15793 14.044 4.96103 13.5708 4.96103 13.018V1.96246C4.96103 1.40968 5.15793 0.936473 5.55173 0.542829C5.94553 0.149184 6.41893 -0.0476379 6.97192 -0.0476379H18.0318C18.5848 -0.0476379 19.0582 0.149184 19.452 0.542829C19.8458 0.936473 20.0427 1.40968 20.0427 1.96246V13.018C20.0427 13.5708 19.8458 14.044 19.452 14.4376C19.0582 14.8313 18.5848 15.0281 18.0318 15.0281H6.97192ZM6.97192 13.018H18.0318V1.96246H6.97192V13.018Z"/>
                                                        <path d="M13.3908 3.24116C13.4092 3.16418 13.3986 3.08393 13.3604 3.01289C13.3223 2.94184 13.2589 2.88399 13.1799 2.84831C13.101 2.81263 13.011 2.80113 12.924 2.81559C12.8369 2.83005 12.7577 2.86967 12.6986 2.92829L8.14504 7.45239C8.09333 7.50378 8.05946 7.56738 8.04752 7.6355C8.03557 7.70363 8.04607 7.77337 8.07773 7.83631C8.10939 7.89925 8.16087 7.9527 8.22596 7.9902C8.29104 8.02771 8.36694 8.04766 8.4445 8.04767H11.9652L11.2661 10.9493C11.2476 11.0263 11.2583 11.1065 11.2964 11.1776C11.3346 11.2486 11.398 11.3065 11.4769 11.3421C11.5559 11.3778 11.6459 11.3893 11.7329 11.3749C11.8199 11.3604 11.8992 11.3208 11.9583 11.2622L16.5118 6.73806C16.5635 6.68667 16.5974 6.62307 16.6094 6.55495C16.6213 6.48682 16.6108 6.41708 16.5791 6.35414C16.5475 6.2912 16.496 6.23775 16.4309 6.20024C16.3658 6.16274 16.2899 6.14278 16.2124 6.14278H12.6917L13.3908 3.24116Z"/>
                                                        </g>
                                                        <defs>
                                                        <clipPath id="clip0_125_7">
                                                        <rect width="20" height="20" fill="white"/>
                                                        </clipPath>
                                                        </defs>
                                                    </svg>
                                                    Practice flashcards
                                                </div>
                                            </Show>
                                            <div onClick={() => deleteUnit(unit.id, unit.type)} class="rounded-bl-md rounded-br-md flex gap-2 items-center cursor-pointer hover:bg-tertiary-2  w-full h-full p-3">
                                                <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 18 18" fill="none">
                                                    <g clip-path="url(#clip0_145_212)">
                                                    <path d="M3.84375 18C3.27656 18 2.79102 17.8042 2.38711 17.4125C1.9832 17.0208 1.78125 16.55 1.78125 16V3C1.48906 3 1.24414 2.90417 1.04648 2.7125C0.848828 2.52083 0.75 2.28333 0.75 2C0.75 1.71667 0.848828 1.47917 1.04648 1.2875C1.24414 1.09583 1.48906 1 1.78125 1H5.90625C5.90625 0.716667 6.00508 0.479167 6.20273 0.2875C6.40039 0.0958333 6.64531 0 6.9375 0H11.0625C11.3547 0 11.5996 0.0958333 11.7973 0.2875C11.9949 0.479167 12.0937 0.716667 12.0937 1H16.2187C16.5109 1 16.7559 1.09583 16.9535 1.2875C17.1512 1.47917 17.25 1.71667 17.25 2C17.25 2.28333 17.1512 2.52083 16.9535 2.7125C16.7559 2.90417 16.5109 3 16.2187 3V16C16.2187 16.55 16.0168 17.0208 15.6129 17.4125C15.209 17.8042 14.7234 18 14.1562 18H3.84375ZM14.1562 3H3.84375V16H14.1562V3ZM6.9375 14C7.22969 14 7.47461 13.9042 7.67227 13.7125C7.86992 13.5208 7.96875 13.2833 7.96875 13V6C7.96875 5.71667 7.86992 5.47917 7.67227 5.2875C7.47461 5.09583 7.22969 5 6.9375 5C6.64531 5 6.40039 5.09583 6.20273 5.2875C6.00508 5.47917 5.90625 5.71667 5.90625 6V13C5.90625 13.2833 6.00508 13.5208 6.20273 13.7125C6.40039 13.9042 6.64531 14 6.9375 14ZM11.0625 14C11.3547 14 11.5996 13.9042 11.7973 13.7125C11.9949 13.5208 12.0937 13.2833 12.0937 13V6C12.0937 5.71667 11.9949 5.47917 11.7973 5.2875C11.5996 5.09583 11.3547 5 11.0625 5C10.7703 5 10.5254 5.09583 10.3277 5.2875C10.1301 5.47917 10.0312 5.71667 10.0312 6V13C10.0312 13.2833 10.1301 13.5208 10.3277 13.7125C10.5254 13.9042 10.7703 14 11.0625 14Z" fill="#39393A"/>
                                                    </g>
                                                    <defs>
                                                    <clipPath id="clip0_145_212">
                                                    <rect width="18" height="18" fill="white"/>
                                                    </clipPath>
                                                    </defs>
                                                </svg>
                                                Delete
                                            </div>
                                        </div>
                                    </Show>
                                </div>
                            )}
                        </For>
                    </Show>
                </div>
            </div>
        </div>
        </>
    );
}