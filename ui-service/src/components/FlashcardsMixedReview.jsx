import { createSignal, Switch, Match, createResource, Show } from "solid-js";


const getFlashcards = async (folderId) => {
    const baseUrl = 'http://localhost:8888/api/content/flashcards';
    let paramsToSend;
    paramsToSend = new URLSearchParams({
        user_id: "23da4be0-70fd-439b-b984-aaf729959e9a",
        folder_id: folderId
    });

    const urlWithParams = `${baseUrl}?${paramsToSend}`;
    const res = await fetch(urlWithParams);
    if (!res.ok) {
        throw new Error('Failed to fetch flashcards');
    }
    let data = await res.json();
    data["total_flashcards"] = data.flashcards.length;
    console.log(data);
    return data;
};


export default function FlashcardsMixedReview(props) {
    const [flashcardDeck, { mutate: mutateFlashcardDeck, fetcher }] = createResource(
        () => props.folderId,
        getFlashcards
    );
    const [answerDisplay, setAnswerDisplay] = createSignal(false);

    const clickShowAnswer = () => {
        setAnswerDisplay(!answerDisplay());
    };

    // Function to check if two dates are the same day
    function isToday(dateString) {
        const today = new Date();
        const reviewDate = new Date(dateString);
        return today.getFullYear() === reviewDate.getFullYear() &&
            today.getMonth() === reviewDate.getMonth() &&
            today.getDate() === reviewDate.getDate();
    }

    // Function to sort flashcards by due date
    function sortFlashcardsByDueDate(flashcards) {
        return flashcards.slice().sort((a, b) => {
            if (!a.next_review && !b.next_review) return 0;   // both null -> keep order
            if (!a.next_review) return -1; // a has no date -> comes first
            if (!b.next_review) return 1;  // b has no date -> comes first
            return new Date(a.next_review) - new Date(b.next_review);
        });
    }

    function getTimeAtNextReview(seconds) {
        if (seconds < 60) {
            return `${seconds} s`;
        } else if (seconds < 3600) { // under 1 hour
            const minutes = Math.floor(seconds / 60);
            return `${minutes} min`;
        } else if (seconds < 86400) { // under 1 day
            const hours = Math.floor(seconds / 3600);
            return `${hours} h`;
        } else if (seconds < 2592000) { // under 30 days
            const days = Math.floor(seconds / 86400);
            return `${days} d`;
        } else if (seconds < 31536000) { // under 1 year
            const months = Math.floor(seconds / 2592000);
            return `${months} mo`;
        } else {
            const years = Math.floor(seconds / 31536000);
            return `${years} y`;
        }
    }    

    const reviewFlashcard = async (rating) => {
        const flashCardId = flashcardDeck().flashcards[0].id;
        console.log(JSON.stringify({
            "flashcard_id": flashCardId,
            "rating": rating,
            "user_id": "23da4be0-70fd-439b-b984-aaf729959e9a"
        }));

        const res = await fetch("http://localhost:8888/api/content/review-flashcard", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                "flashcard_id": flashCardId,
                "rating": rating,
                "user_id": "23da4be0-70fd-439b-b984-aaf729959e9a"
            })
        });
        const resData = await res.json();
        console.log("resData", resData)

        let updatedFlashcards;
        const flashcards = flashcardDeck().flashcards;
        flashcards[0]["next_review"] = resData.due_date;
        console.log("next_review", resData.due_date)
        console.log("with next_review", flashcards)
        if (!isToday(resData.due_date)) {
            updatedFlashcards = flashcards.filter(card => card.id !== flashCardId);
        } else {
            flashcards[0]["future_ratings_time"] = resData.future_ratings_time;
            updatedFlashcards = sortFlashcardsByDueDate(flashcards);
        }

        // Update the resource
        console.log(updatedFlashcards)
        mutateFlashcardDeck(prev => ({
            ...prev,
            flashcards: updatedFlashcards,
        }));
        console.log(flashcardDeck())
        setAnswerDisplay(false);
    };

    return (
        <div class="fixed inset-0 z-51 bg-tertiary-100/80 flex items-center justify-center w-full h-full flex justify-center items-center">
            <div onClick={() => props.setFlashcardsReview(false)} class="cursor-pointer top-5 right-5 absolute fill-primary/50 hover:fill-primary">
                <svg xmlns="http://www.w3.org/2000/svg" width="45" height="45" viewBox="0 0 40 40">
                    <path d="M20 21.1796L25.4104 26.5896C25.5662 26.7457 25.7575 26.829 25.9842 26.8396C26.2106 26.8504 26.4124 26.7671 26.5896 26.5896C26.7671 26.4124 26.8558 26.2158 26.8558 26C26.8558 25.7842 26.7671 25.5876 26.5896 25.4104L21.1796 20L26.5896 14.5896C26.7457 14.4338 26.829 14.2425 26.8396 14.0158C26.8504 13.7894 26.7671 13.5876 26.5896 13.4104C26.4124 13.2329 26.2158 13.1442 26 13.1442C25.7842 13.1442 25.5876 13.2329 25.4104 13.4104L20 18.8204L14.5896 13.4104C14.4338 13.2543 14.2425 13.171 14.0158 13.1604C13.7894 13.1496 13.5876 13.2329 13.4104 13.4104C13.2329 13.5876 13.1442 13.7842 13.1442 14C13.1442 14.2158 13.2329 14.4124 13.4104 14.5896L18.8204 20L13.4104 25.4104C13.2543 25.5663 13.171 25.7575 13.1604 25.9842C13.1496 26.2106 13.2329 26.4124 13.4104 26.5896C13.5876 26.7671 13.7842 26.8558 14 26.8558C14.2158 26.8558 14.4124 26.7671 14.5896 26.5896L20 21.1796ZM20.0054 35C17.9313 35 15.9811 34.6064 14.155 33.8192C12.3292 33.0319 10.7408 31.9636 9.39 30.6142C8.03917 29.2647 6.96986 27.6778 6.18208 25.8533C5.39403 24.0292 5 22.0799 5 20.0054C5 17.9313 5.39361 15.9811 6.18083 14.155C6.96806 12.3292 8.03639 10.7408 9.38583 9.39C10.7353 8.03917 12.3222 6.96986 14.1467 6.18208C15.9708 5.39403 17.9201 5 19.9946 5C22.0688 5 24.0189 5.39361 25.845 6.18083C27.6708 6.96806 29.2592 8.03639 30.61 9.38583C31.9608 10.7353 33.0301 12.3222 33.8179 14.1467C34.606 15.9708 35 17.9201 35 19.9946C35 22.0688 34.6064 24.0189 33.8192 25.845C33.0319 27.6708 31.9636 29.2592 30.6142 30.61C29.2647 31.9608 27.6778 33.0301 25.8533 33.8179C24.0292 34.606 22.0799 35 20.0054 35ZM20 33.3333C23.7222 33.3333 26.875 32.0417 29.4583 29.4583C32.0417 26.875 33.3333 23.7222 33.3333 20C33.3333 16.2778 32.0417 13.125 29.4583 10.5417C26.875 7.95833 23.7222 6.66667 20 6.66667C16.2778 6.66667 13.125 7.95833 10.5417 10.5417C7.95833 13.125 6.66667 16.2778 6.66667 20C6.66667 23.7222 7.95833 26.875 10.5417 29.4583C13.125 32.0417 16.2778 33.3333 20 33.3333Z"/>
                </svg>
            </div>
            <div class="shadow-lg flex flex-col justify-end items-end w-[85%] lg:w-[65%] h-[75%] border border-tertiary-40 rounded-lg bg-primary">
                <Show when={flashcardDeck() && flashcardDeck().total_flashcards !== flashcardDeck().flashcards.length}>
                    <div class="bg-primary border-b border-tertiary-40 w-full rounded-tl-md rounded-tr-md">
                            <div
                                class={`transition-width duration-500 text-xs text-primary/70 rounded-tl-md bg-secondary text-right pr-2 ${
                                    (1 - flashcardDeck().flashcards.length / flashcardDeck().total_flashcards) * 100 == 100 || flashcardDeck().flashcards.length == 0
                                    ? 'rounded-tr-md'
                                    : ''
                                }`}
                                style={{
                                    width: `${(1 - flashcardDeck().flashcards.length / flashcardDeck().total_flashcards) * 100}%`
                                }}
                                >
                                {flashcardDeck().total_flashcards - flashcardDeck().flashcards.length}/{flashcardDeck().total_flashcards}
                            </div>
                    </div>
                </Show>
                <Switch>
                    <Match when={flashcardDeck() && flashcardDeck().flashcards.length === 0}>
                        <div class="text-center flex flex-col w-full h-full justify-center items-center text-tertiary-100 font-medium text-lg">
                            <span class="flex w-full h-full justify-center items-center text-tertiary-100 font-medium text-xl">
                                You have finished this deck.<br/>
                                Congratulations!
                            </span>
                        </div>
                    </Match>
                    <Match when={answerDisplay()}>
                        <div class="p-5 text-center flex flex-col w-full h-full justify-center items-center text-tertiary-100 font-medium text-lg">
                            <span class="flex border-b border-tertiary-40 w-full h-full justify-center items-center text-tertiary-100 font-medium text-lg">
                                {flashcardDeck().flashcards[0].content.front}
                            </span>
                            <span class="text-center flex w-full h-full justify-center items-center text-tertiary-100 font-medium text-lg">
                                {flashcardDeck().flashcards[0].content.back}
                            </span>
                        </div>
                        <div class="text-primary flex w-full">
                            <button onClick={() => reviewFlashcard(1)} class="bg-tertiary-red-75 rounded-bl-md w-full h-20 cursor-pointer hover:bg-tertiary-red-80">
                                Again<br/>
                                <span class="text-xs">
                                    {getTimeAtNextReview(flashcardDeck().flashcards[0]["future_ratings_time"][1])}
                                </span>
                            </button>
                            <button onClick={() => reviewFlashcard(2)} class="bg-tertiary-red-60 w-full h-20 cursor-pointer hover:bg-tertiary-red-65">
                                Hard<br/>
                                <span class="text-xs">
                                    {getTimeAtNextReview(flashcardDeck().flashcards[0]["future_ratings_time"][2])}
                                </span>
                            </button>
                            <button onClick={() => reviewFlashcard(3)} class="bg-tertiary-green-60 w-full h-20 cursor-pointer hover:bg-tertiary-green-65">
                                Good<br/>
                                <span class="text-xs">
                                    {getTimeAtNextReview(flashcardDeck().flashcards[0]["future_ratings_time"][3])}
                                </span>
                            </button>
                            <button onClick={() => reviewFlashcard(4)} class="rounded-br-md bg-tertiary-green-95 w-full h-20 cursor-pointer hover:bg-tertiary-green-100">
                                Easy<br/>
                                <span class="text-xs">
                                    {getTimeAtNextReview(flashcardDeck().flashcards[0]["future_ratings_time"][4])}
                                </span>
                            </button>
                        </div>
                    </Match>
                    <Match when={!answerDisplay() && flashcardDeck()}>
                        <span class="p-5 text-center flex w-full h-full justify-center items-center text-tertiary-100 font-medium text-lg">
                            {flashcardDeck().flashcards[0].content.front}
                        </span>
                        <button onClick={clickShowAnswer} class="text-tertiary-100 bg-primary border-t border-tertiary-40 rounded-br-md rounded-bl-md w-full h-20 cursor-pointer hover:bg-tertiary-2">
                            <span class="text-sm">Show answer</span>
                        </button>
                    </Match>
                </Switch>
            </div>
        </div>
    );
}