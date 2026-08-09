import type { JSX } from "solid-js";
import { useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { FlashcardsReview } from "./FlashcardsReview";

export default function FlashcardsPage(): JSX.Element {
  const params = useParams<{ id: string }>();

  return (
    <AppShell fillsViewport>
      <div class="review">
        <FlashcardsReview scope="flashcard_deck" scopeId={params.id} />
      </div>
    </AppShell>
  );
}
