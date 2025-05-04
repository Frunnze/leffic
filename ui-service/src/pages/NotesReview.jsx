import { createSignal, Switch, Match, createResource} from "solid-js";
import LeftNavBar from "../components/LeftNavBar";
import { useParams } from "@solidjs/router";


const getNotes = async (notesId) => {    
    const baseUrl = 'http://localhost:8888/api/content/flashcards';
    const paramsToSend = new URLSearchParams({
        flashcard_deck_id: flashcardDeckId,
        user_id: "23da4be0-70fd-439b-b984-aaf729959e9a"
    });
    const urlWithParams = `${baseUrl}?${paramsToSend}`;

    const res = await fetch(urlWithParams);
    if (!res.ok) {
        throw new Error('Failed to fetch flashcards');
    }
    const data = await res.json();
    console.log(data);
    return data;
};


export default function FlashcardsReview() {
    const params = useParams();
    const [flashcardDeck, { mutate: mutateFlashcardDeck, fetcher }] = createResource(
        () => params.id,
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
        <div class="flex h-screen text-tertiary-100">
            <LeftNavBar/>
            <div class="ml-17 w-full h-full bg-primary flex justify-center items-center text-primary">
                <div class="shadow-sm flex flex-col justify-end items-end w-[85%] lg:w-[65%] h-[75%] border border-tertiary-40 rounded-lg bg-primary">
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
                            <div class="flex w-full">
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
        </div>
    );
}