import { createSignal, Switch, Match, createResource, Show, onMount } from "solid-js";
import { apiRequest } from "../utils/apiRequest";
import { useParams } from "@solidjs/router";


const getFlashcards = async (params) => {
    const res = await apiRequest({
        endpoint: `/api/content/flashcards?${new URLSearchParams(params).toString()}`
    })
    if (!res.ok) return null;
    let data = await res.json();
    if (data.total_flashcards === 0) return null;
    console.log("deck first", data)
    return data;
};

const getRatingsTimes = async (card) => {
    const res = await apiRequest({
        method: "POST",
        endpoint: "/api/scheduler/public/ratings-times",
        body: { card: card }
    });
    if (!res.ok) return null;
    let data = await res.json();
    console.log(data);
    return data;
};

export default function FlashcardsMainReview(props) {
    const params = useParams();
    const [flashcardDeck, setFlashcardDeck ] = createSignal();
    const [answerDisplay, setAnswerDisplay] = createSignal(false);
    const [completedFlahscards, setCompletedFlahscards] = createSignal(0);
    const [ratingsTimes, setRatingsTimes ] = createSignal();
    const getFlashcardsReqParams = {[`${props.flashcardsOrigin}_id`]: params.id};

    onMount(async () => {
        const flashcardDeck = await getFlashcards(getFlashcardsReqParams);
        if (flashcardDeck) {
            const firstFlashcardRatingsTimes = await getRatingsTimes(flashcardDeck.flashcards[0].fsrs_card);
            setRatingsTimes(firstFlashcardRatingsTimes);
            setFlashcardDeck(flashcardDeck);
        }
    });

    const clickShowAnswer = async () => {
        setAnswerDisplay(!answerDisplay());

        // Get ratings times for the next flashcard
        const resRatingsTimes = await getRatingsTimes(flashcardDeck().flashcards[0].fsrs_card);
        if (resRatingsTimes) setRatingsTimes(resRatingsTimes);
    };

    function sortFlashcardsByDueDate(flashcards) {
        return flashcards.slice().sort((a, b) => {
            if (!a.next_review && !b.next_review) return 0;
            if (!a.next_review) return -1;
            if (!b.next_review) return 1;
            return new Date(a.next_review) - new Date(b.next_review);
        });
    }

    function getTimeAtNextReview(seconds) {
        if (seconds < 60) {
            return `${seconds} s`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            return `${minutes} min`;
        } else if (seconds < 86400) {
            const hours = Math.floor(seconds / 3600);
            return `${hours} h`;
        } else if (seconds < 2592000) {
            const days = Math.floor(seconds / 86400);
            return `${days} d`;
        } else if (seconds < 31536000) {
            const months = Math.floor(seconds / 2592000);
            return `${months} mo`;
        } else {
            const years = Math.floor(seconds / 31536000);
            return `${years} y`;
        }
    };

    function isToday(date) {
        const today = new Date();
        return (
            date.getUTCDate() === today.getUTCDate() &&
            date.getUTCMonth() === today.getUTCMonth() &&
            date.getUTCFullYear() === today.getUTCFullYear()
        );
    }

    const reviewFlashcard = async (rating) => {
        // Review the flashcard
        const res = await apiRequest({
            endpoint: "/api/content/review-flashcard",
            method: "POST",
            body: {
                "flashcard_id": flashcardDeck().flashcards[0].id,
                "rating": rating
            }
        });
        const resData = await res.json();

        // Check if the next review date of the flashcard is not today
        // Count the progress if it is not today
        const dueDate = new Date(resData.due_date);
        if (!isToday(dueDate)) setCompletedFlahscards(completedFlahscards()+1);

        // Eliminate the reviewed card if it is only one in the flashcards array
        // Get the new flashcards page of today
        if (flashcardDeck().flashcards.length == 1) {
            const flashcardDeckPage = await getFlashcards(getFlashcardsReqParams);
            if (flashcardDeckPage) {
                setFlashcardDeck(flashcardDeckPage);
            } else {
                flashcardDeck();
            };
            setAnswerDisplay(false);
            return;
        };

        // 
        console.log("AFTER REVIEW", resData)
        let updatedFlashcards;
        let flashcards = flashcardDeck().flashcards.slice();
        flashcards[0] = {
            ...flashcards[0],
            next_review: resData.due_date,
            fsrs_card: resData.new_fsrs_card
        };

        const lastFlashcard = flashcards[flashcards.length - 1];
        if (lastFlashcard.next_review) {
            const nextReviewDateOfLastFlashcard = new Date(lastFlashcard.next_review);
            if (dueDate >= nextReviewDateOfLastFlashcard) {
                updatedFlashcards = flashcards.filter(card => card.id !== flashcardDeck().flashcards[0].id);
            } else {
                updatedFlashcards = sortFlashcardsByDueDate(flashcards);
            };
        } else {
            updatedFlashcards = flashcards.filter(card => card.id !== flashcardDeck().flashcards[0].id);
        };

        setFlashcardDeck(prev => ({
            ...prev,
            flashcards: updatedFlashcards,
        }));
        setAnswerDisplay(false);
    };

    return (
        <div class="shadow-lg flex flex-col justify-end items-end w-[85%] lg:w-[65%] h-[75%] border border-tertiary-40 rounded-lg bg-primary">
            <Show when={flashcardDeck()}>
                <div class="relative bg-primary border-b border-tertiary-40 w-full h-5 rounded-tl-md rounded-tr-md">
                        <span class="absolute font-black bg-black right-1/2 left-1/2 top-0 text-xs text-tertiary-100/50">{completedFlahscards()}/{flashcardDeck().total_flashcards}</span>
                        <div
                            class={`h-full transition-width duration-500 rounded-tl-md bg-secondary
                                    ${((completedFlahscards()/flashcardDeck().total_flashcards) * 100 == 100) ? 'rounded-tr-md': ''}`}
                            style={{
                                width: `${Math.min(100, (completedFlahscards() / flashcardDeck().total_flashcards) * 100)}%`
                            }}
                        />
                </div>
            </Show>
            <Switch>
                <Match when={!flashcardDeck() || flashcardDeck().total_flashcards === completedFlahscards()}>
                    <div class="text-center flex flex-col w-full h-full justify-center items-center text-tertiary-100 font-medium text-lg">
                        <span class="flex w-full h-full justify-center items-center text-tertiary-100 font-medium text-xl">
                            Deck is empty!
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
                                {getTimeAtNextReview(ratingsTimes()[1])}
                            </span>
                        </button>
                        <button onClick={() => reviewFlashcard(2)} class="bg-tertiary-red-60 w-full h-20 cursor-pointer hover:bg-tertiary-red-65">
                            Hard<br/>
                            <span class="text-xs">
                                {getTimeAtNextReview(ratingsTimes()[2])}
                            </span>
                        </button>
                        <button onClick={() => reviewFlashcard(3)} class="bg-tertiary-green-60 w-full h-20 cursor-pointer hover:bg-tertiary-green-65">
                            Good<br/>
                            <span class="text-xs">
                                {getTimeAtNextReview(ratingsTimes()[3])}
                            </span>
                        </button>
                        <button onClick={() => reviewFlashcard(4)} class="rounded-br-md bg-tertiary-green-95 w-full h-20 cursor-pointer hover:bg-tertiary-green-100">
                            Easy<br/>
                            <span class="text-xs">
                                {getTimeAtNextReview(ratingsTimes()[4])}
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
    );
}