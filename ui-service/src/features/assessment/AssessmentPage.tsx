import type { JSX } from "solid-js";
import { useNavigate, useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { ReviewBar } from "../../shared/ui/ReviewBar";
import { AssessmentProgress } from "./assessment-progress";
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
        <div class="stage test-stage">
          <AssessmentReview
            scope={props.scope}
            scopeId={params.id}
            progress={AssessmentProgress}
          />
        </div>
      </div>
    </AppShell>
  );
}
