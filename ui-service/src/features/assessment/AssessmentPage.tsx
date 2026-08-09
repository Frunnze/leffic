import type { JSX } from "solid-js";
import { useParams } from "@solidjs/router";
import { AppShell } from "../../shared/ui/AppShell";
import { AssessmentReview } from "./AssessmentReview";

export default function AssessmentPage(): JSX.Element {
  const params = useParams<{ id: string }>();

  return (
    <AppShell>
      <div class="test-stage">
        <AssessmentReview scope="test" scopeId={params.id} />
      </div>
    </AppShell>
  );
}
