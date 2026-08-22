import type { JSX } from "solid-js";
import { useNavigate, useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { ReviewBar } from "../../shared/ui/ReviewBar";
import { FlashcardsReview } from "./FlashcardsReview";

type FlashcardsPageProps = {
  readonly scope: "flashcard_deck" | "folder";
};

export default function FlashcardsPage(props: FlashcardsPageProps): JSX.Element {
  const params = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <AppShell fillsViewport>
      <div class="review-page">
        <ReviewBar title="Flashcards" onClose={() => { navigate(-1); }} />
        <div class="review">
          <FlashcardsReview scope={props.scope} scopeId={params.id} />
        </div>
      </div>
    </AppShell>
  );
}
