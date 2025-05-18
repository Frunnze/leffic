import { createSignal, For } from "solid-js";
import { apiRequest } from "../utils/apiRequest";


export default function ChatBot(props) {
    const [messages, setMessages] = createSignal([
        {
            "role": "assistant",
            "content": "Hi, how can I help you?"
        }
    ]);
    const [input, setInput] = createSignal("");
    const [loading, setLoading] = createSignal(false);

    const sendMessage = async () => {
        const userMessage = input().trim();
        if (!userMessage || loading()) return;

        // Append user message
        setMessages([...messages(), { role: "user", content: userMessage }]);
        setInput("");
        setLoading(true);

        try {
            const res = await apiRequest({
                endpoint: "/api/files/chat",
                method: "POST",
                body: { conversation: messages() }
            });
            const data = await res.json();
            console.log("DATA FROM CHAT", data)
            console.log("MESSAGES", messages())

            // Append bot response
            setMessages([...messages(), 
                { role: "assistant", content: data.answer || "Sorry, no response." }
            ]);
        } catch (error) {
            setMessages([...messages(), 
                { role: "user", content: userMessage },
                { role: "assistant", content: "Something went wrong. Try again." }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div class="text-base ml-17 flex flex-1 flex-col z-10 absolute h-screen w-100 max-w-lg mx-auto shadow-md border border-gray-200 border-l-0">
            <div class="flex px-2 justify-center gap-x-2 items-center border-b border-tertiary-10 text-center text-teratiary-100 h-10 bg-primary text-primary">
                <svg class="fill-secondary" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#1f1f1f"><path d="M880-80 720-240H320q-33 0-56.5-23.5T240-320v-40h440q33 0 56.5-23.5T760-440v-280h40q33 0 56.5 23.5T880-640v560ZM160-473l47-47h393v-280H160v327ZM80-280v-520q0-33 23.5-56.5T160-880h440q33 0 56.5 23.5T680-800v280q0 33-23.5 56.5T600-440H240L80-280Zm80-240v-280 280Z"/></svg>
                <span class="text-secondary">Ask</span>
                <div onclick={props.closeBot} class="absolute top-1 right-1 cursor-pointer fill-tertiary-100/50 hover:fill-tertiary-100">
                    <svg xmlns="http://www.w3.org/2000/svg" height="25px" viewBox="0 -960 960 960" width="25px"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/></svg>
                </div>
            </div>
            <div class="overflow-scroll no-scrollbar flex flex-col p-5 bg-primary h-full overflow-y-auto space-y-3 no-scrollbar">
                <For each={messages()}>
                    {(msg, index) => (
                        <div class={`flex w-full p-2 ${msg.role === "assistant" ? "justify-start" : "justify-end"}`}>
                            <div class={`shadow p-4 flex items-center justify-center rounded-4xl w-[75%] text-primary text-sm ${
                                            msg.role === "assistant"
                                                ? "bg-secondary text-primary"
                                                : "text-primary bg-tertiary-100/50"
                                        }`}>
                                {msg.content}
                            </div>
                        </div>
                    )}
                </For>
            </div>
            <div class="flex">
                <input
                    type="text"
                    value={input()}
                    onInput={(e) => setInput(e.currentTarget.value)}
                    placeholder="Ask anything ..."
                    class="bg-primary border-1 border-tertiary-10 flex-1 py-2 px-2 text-sm focus:outline-none focus:ring-blue-400"
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                />
                <button
                    onClick={sendMessage}
                    class="cursor-pointer w-25 h-20 py-2 bg-secondary text-white hover:bg-blue-600 text-sm"
                    disabled={loading()}
                >
                    Send
                </button>
            </div>
        </div>
    );
}
