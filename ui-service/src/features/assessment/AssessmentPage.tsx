import type { JSX } from "solid-js";
import { useNavigate, useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { ReviewBar } from "../../shared/ui/ReviewBar";
import { AssessmentReview } from "./AssessmentReview";

type AssessmentPageProps = {
  readonly scope: "test" | "folder";
};

export default function AssessmentPage(
  props: AssessmentPageProps,
): JSX.Element {
  const params = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <AppShell fillsViewport>
      <div class="review-page">
        <ReviewBar title="Test" onClose={() => { navigate(-1); }} />
        <div class="test-stage">
          <AssessmentReview scope={props.scope} scopeId={params.id} />
        </div>
      </div>
    </AppShell>
  );
}
