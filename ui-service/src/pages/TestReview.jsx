import LeftNavBar from "../components/LeftNavBar";
import TestMainReview from "../components/TestMainReview";


export default function TestReview() {
  return (
        <div class="text-tertiary-100 min-h-screen bg-secondary/10">
            <LeftNavBar/>
            <div class="min-h-screen ml-17 p-10 lg:px-30 flex justify-center items-center">
                <TestMainReview testReviewOrigin="test"/>
            </div>
        </div>
    );
}