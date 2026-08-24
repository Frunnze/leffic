/* @refresh reload */
import { render } from "solid-js/web";

import "./index.css";
import { App } from "./App";
import { Theme } from "./shared/ui/theme";
import { ToastProvider } from "./shared/notifications/ToastContext";
import { AskProvider } from "./shared/chatbot/AskContext";
import { GenerationProvider } from "./features/folder/import/GenerationContext";

Theme.apply(Theme.lastPainted());

const root = document.getElementById("root");

if (!(root instanceof HTMLElement)) {
  throw new Error("Root element #root is missing from index.html");
}

render(
  () => (
    <ToastProvider>
      <GenerationProvider>
        <AskProvider>
          <App />
        </AskProvider>
      </GenerationProvider>
    </ToastProvider>
  ),
  root,
);
