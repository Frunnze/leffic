import { Show, type JSX } from "solid-js";
import { AssessmentReview } from "../assessment/AssessmentReview";
import { FlashcardsReview } from "../flashcards/FlashcardsReview";
import { ReviewOverlay } from "../../shared/ui/ReviewOverlay";

export type OpenReview = "none" | "flashcards" | "assessment";

export type FolderReviewOverlaysProps = {
  readonly folderId: string;
  readonly openReview: OpenReview;
  readonly onClose: () => void;
};

export function FolderReviewOverlays(
  props: FolderReviewOverlaysProps,
): JSX.Element {
  return (
    <>
      <Show when={props.openReview === "flashcards"}>
        <ReviewOverlay title="Flashcards" onClose={props.onClose}>
          <div class="review">
            <FlashcardsReview scope="folder" scopeId={props.folderId} />
          </div>
        </ReviewOverlay>
      </Show>

      <Show when={props.openReview === "assessment"}>
        <ReviewOverlay title="Test" onClose={props.onClose}>
          <div class="test-stage">
            <AssessmentReview scope="folder" scopeId={props.folderId} />
          </div>
        </ReviewOverlay>
      </Show>
    </>
  );
}
