import { createSignal, createEffect, onCleanup, For } from "solid-js";


export default function GeneralDropdown(props) {
    const [dropdownRef, setDropdownRef] = createSignal(null);
    createEffect(() => {
        if (props.dropdownState()) {
            const handleClickOutside = (e) => {
                if (dropdownRef() && !dropdownRef().contains(e.target)) {
                    props.setDropdownState(false);
                }
            };     
            document.addEventListener("click", handleClickOutside);
            onCleanup(() => {
                document.removeEventListener("click", handleClickOutside);
            });
        }
    });
    

    return (
        <Show when={props.dropdownState() == true}>
            <div ref={setDropdownRef} class={`${props.position} text-tertiary-100 absolute font-medium border border-tertiary-10 bg-primary flex flex-col justify-content items-center text-sm z-50 mt-2 w-45 rounded-md shadow-lg`}>
                <For each={props.dropDownItems}>
                    { (item, index) => 
                        (
                            <div onclick={item.trigger} class={`${index() === props.dropDownItems.length-1 ? "rounded-bl-md rounded-br-md": "border-b border-tertiary-10"} flex gap-2 items-center cursor-pointer hover:bg-tertiary-2  w-full h-full p-3`}>
                                {item.svg}
                                {item.label}
                            </div>
                        )
                    }
                </For>
            </div>
        </Show>
    );
};