/* @refresh reload */
import { render } from "solid-js/web";

import "./index.css";
import { App } from "./App";
import { ToastProvider } from "./features/notifications/ToastContext";

const root = document.getElementById("root");

if (!(root instanceof HTMLElement)) {
  throw new Error("Root element #root is missing from index.html");
}

render(
  () => (
    <ToastProvider>
      <App />
    </ToastProvider>
  ),
  root,
);
