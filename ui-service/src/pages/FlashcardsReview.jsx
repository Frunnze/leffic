import FlashcardsMainReview from "../components/FlashcardsMainReview";
import LeftNavBar from "../components/LeftNavBar";


export default function FlashcardsReview() {
    return (
        <div class="ml-17 flex h-screen text-tertiary-100 justify-center items-center bg-secondary/10">
            <LeftNavBar/>
            <FlashcardsMainReview flashcardsOrigin="flashcard_deck"/>
        </div>
    );
};