import { Show, createResource, createSignal, type JSX } from "solid-js";
import { useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { Icon } from "../../shared/ui/icons/Icon";
import { useToasts } from "../notifications/ToastContext";
import { NotesApi } from "./notes-api";

type ReadState = "unread" | "saving" | "read";

export default function NotePage(): JSX.Element {
  const params = useParams<{ id: string }>();
  const [note] = createResource(() => params.id, NotesApi.note);
  const toasts = useToasts();
  const [pendingState, setPendingState] = createSignal<ReadState | null>(null);

  const readState = (): ReadState => {
    const pending = pendingState();
    if (pending !== null) return pending;

    return note()?.isRead === true ? "read" : "unread";
  };

  const markAsRead = async (): Promise<void> => {
    setPendingState("saving");

    try {
      await NotesApi.markAsRead(params.id);
      setPendingState("read");
    } catch {
      setPendingState(null);
      toasts.show({
        tone: "failure",
        title: "Couldn't mark the note as read",
        detail: "The note stayed in your due list. Try again.",
      });
    }
  };

  const buttonLabel = (): string => {
    if (readState() === "saving") return "Marking…";
    if (readState() === "read") return "Marked as read";

    return "Mark as read";
  };

  const readingLabel = (minutes: number | null): string =>
    minutes === null ? "Generated note" : `${minutes} min read`;

  return (
    <AppShell>
      <div class="notes-stage">
        <Show
          when={note()}
          fallback={
            <article class="note-card">
              <p class="note-meta">Loading the note…</p>
            </article>
          }
        >
          {(loaded) => (
            <article class="note-card">
              <header class="note-head">
                <h1 class="note-title">{loaded().name}</h1>
                <span class="note-meta">
                  {readingLabel(loaded().readingMinutes)}
                </span>
              </header>

              <div class="note-body" innerHTML={loaded().content} />

              <footer class="note-foot">
                <button
                  class="btn"
                  classList={{
                    "btn-primary": readState() !== "read",
                    "is-done": readState() === "read",
                  }}
                  type="button"
                  disabled={readState() !== "unread"}
                  onClick={() => void markAsRead()}
                >
                  <Icon name={readState() === "read" ? "success" : "check"} size="sm" />
                  {buttonLabel()}
                </button>
              </footer>
            </article>
          )}
        </Show>
      </div>
    </AppShell>
  );
}
