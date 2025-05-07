import { createSignal, createEffect, onCleanup } from "solid-js";


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
            <div ref={setDropdownRef} class="text-tertiary-100 absolute bottom-1 left-17 font-medium border border-tertiary-10 bg-primary flex flex-col justify-content items-center text-sm z-50 mt-2 w-45 origin-top-right rounded-md shadow-lg">
                <div class="rounded-tl-md rounded-tr-md flex gap-2 items-center cursor-pointer hover:bg-tertiary-2  w-full h-full border-b border-tertiary-10 p-3">
                    {props.option2Svg}
                    {props.option2Label}
                </div>
                <div onclick={() => props.optionOneFun()} class="rounded-bl-md rounded-br-md flex gap-2 items-center cursor-pointer hover:bg-tertiary-2  w-full h-full p-3">
                    {props.optionOneSvg}
                    {props.optionOneLabel}
                </div>
            </div>
        </Show>
    );
}