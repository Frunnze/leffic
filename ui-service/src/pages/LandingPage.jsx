import { useNavigate } from "@solidjs/router";

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div class="flex flex-col justify-center items-center p-10 bg-primary w-full min-h-screen">
            <svg class="flex-none" xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 35 35" fill="none">
                <path d="M18.5208 27.7083H26.6875C26.5174 28.3403 26.2257 28.8507 25.8125 29.2396C25.3993 29.6285 24.8646 29.8715 24.2083 29.9687L8.31249 31.901C7.51041 32.0226 6.78732 31.8342 6.14322 31.3359C5.49913 30.8377 5.12847 30.1875 5.03124 29.3854L3.09895 13.4531C3.00173 12.651 3.19617 11.934 3.68228 11.3021C4.1684 10.6701 4.81249 10.3056 5.61458 10.2083L7.29166 9.98958V12.9062L5.97916 13.0885L7.94791 29.0208L18.5208 27.7083ZM13.125 24.7917C12.3229 24.7917 11.6363 24.5061 11.0651 23.9349C10.4939 23.3637 10.2083 22.6771 10.2083 21.875V5.83333C10.2083 5.03125 10.4939 4.34462 11.0651 3.77344C11.6363 3.20225 12.3229 2.91666 13.125 2.91666H29.1667C29.9687 2.91666 30.6554 3.20225 31.2266 3.77344C31.7977 4.34462 32.0833 5.03125 32.0833 5.83333V21.875C32.0833 22.6771 31.7977 23.3637 31.2266 23.9349C30.6554 24.5061 29.9687 24.7917 29.1667 24.7917H13.125ZM13.125 21.875H29.1667V5.83333H13.125V21.875Z" fill="#3083DC"/>
                <path d="M22.4873 8.60432C22.5131 8.49654 22.4982 8.38419 22.4448 8.28473C22.3914 8.18527 22.3026 8.10427 22.1921 8.05432C22.0816 8.00437 21.9556 7.98827 21.8338 8.00851C21.7119 8.02876 21.601 8.08423 21.5183 8.16629L15.1432 14.5C15.0708 14.572 15.0234 14.661 15.0067 14.7564C14.99 14.8518 15.0047 14.9494 15.049 15.0375C15.0933 15.1256 15.1654 15.2005 15.2565 15.253C15.3476 15.3055 15.4539 15.3334 15.5625 15.3334H20.4915L19.5127 19.3957C19.4869 19.5035 19.5018 19.6158 19.5552 19.7153C19.6086 19.8147 19.6974 19.8957 19.8079 19.9457C19.9184 19.9956 20.0444 20.0117 20.1662 19.9915C20.2881 19.9712 20.399 19.9158 20.4817 19.8337L26.8568 13.5C26.9292 13.428 26.9766 13.339 26.9933 13.2436C27.01 13.1482 26.9953 13.0506 26.951 12.9625C26.9067 12.8744 26.8346 12.7995 26.7435 12.747C26.6524 12.6945 26.5461 12.6666 26.4375 12.6666H21.5085L22.4873 8.60432Z" fill="#3083DC"/>
            </svg>
            <span class="text-5xl font-semibold text-secondary">Leffic</span>
            <span class="mt-5 text-2xl font-semibold text-secondary">Learn efficiently</span>
            <button onClick={() => navigate("/login")} class="text-xl mt-4 w-50 shadow-secondary cursor-pointer rounded-full bg-secondary py-2 px-4 border border-transparent text-center text-primary transition-all shadow-sm hover:shadow-lg hover:bg-secondary" type="button">
                Try
            </button>
            {/* <div class="text-primary text-sm pt-10 pl-30 pr-10 absolute flex items-center justify-center rounded-full bg-secondary h-[40%] w-[40%] -top-25 -left-25"/> */}
            <div class="flex flex-col md:flex-row gap-5 mt-15 justify-between text-tertiary-100/90">
                <div class="shadow-lg flex flex-1 flex-col border-2 p-4 border-secondary rounded">
                    <span class="font-semibold text-secondary">
                        Scientific learning methods
                    </span>
                    <span>
                        Use evidence-based learning methods such as
                        spaced repetition, active recall, and interleaving.
                    </span>
                </div>
                <div class="shadow-lg flex flex-1 flex-col border-2 p-4 border-secondary rounded">
                    <span class="font-semibold text-secondary">
                        AI Automation
                    </span>
                    <span>
                        Generate flashcards, notes and tests with AI from 
                        imported files, links, topics, or text.
                    </span>
                </div>
                <div class="shadow-lg flex flex-1 flex-col border-2 p-4 border-secondary rounded">
                    <span class="font-semibold text-secondary">
                        Review tools
                    </span>
                    <span>
                        Review files, flashcards, tests, and notes. Reduce review time by more than 20% with state-of-the-art scheduling algorithms.
                    </span>
                </div>
            </div>
        </div>
    );
}