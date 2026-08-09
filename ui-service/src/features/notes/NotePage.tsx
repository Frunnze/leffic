import { Show, createResource, type JSX } from "solid-js";
import { useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { Icon } from "../../shared/ui/icons/Icon";
import { NotesApi } from "./notes-api";

export default function NotePage(): JSX.Element {
  const params = useParams<{ id: string }>();
  const [note] = createResource(() => params.id, NotesApi.note);

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
                <button class="btn btn-primary" type="button">
                  <Icon name="check" size="sm" />
                  Mark as read
                </button>
              </footer>
            </article>
          )}
        </Show>
      </div>
    </AppShell>
  );
}
