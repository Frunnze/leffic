import { For, type JSX } from "solid-js";
import { A } from "@solidjs/router";
import { Icon } from "../../shared/ui/icons/Icon";
import { Meter } from "../../shared/ui/Meter";
import type { IconName } from "../../shared/ui/icons/icon-shapes";

type Artefact = {
  readonly icon: IconName;
  readonly name: string;
};

const OUTPUTS: readonly Artefact[] = [
  { icon: "flashcards", name: "30 flashcards" },
  { icon: "note", name: "1 note" },
  { icon: "test", name: "24 questions" },
];

export default function LandingPage(): JSX.Element {
  return (
    <div class="screen">
      <div class="landing">
        <header class="landing-bar">
          <span class="landing-wordmark">
            <Icon name="logo" />
            Leffic
          </span>
          <A class="btn" href="/login">
            Log in
          </A>
        </header>

        <div class="landing-hero">
          <h1 class="landing-title">Learn it once. Remember it for good.</h1>
          <p class="landing-lede">
            Turn any file, link or topic into flashcards, notes and a test — then
            review them exactly when you're about to forget.
          </p>
          <div class="landing-cta">
            <A class="btn btn-primary btn-lg" href="/sign-up">
              Start free
            </A>
          </div>
          <p class="landing-note">
            No card needed. Your first deck takes about a minute.
          </p>
        </div>

        <section class="mechanic" aria-label="How Leffic works">
          <div class="mechanic-step mechanic-source">
            <h2 class="section-label">You drop in</h2>
            <div class="artefact">
              <Icon name="file" />
              <span class="artefact-name">action-potentials.pdf</span>
              <span class="artefact-meta">1.2 MB</span>
            </div>
            <p class="mechanic-note">
              A file, a link, or just the name of a topic.
            </p>
          </div>

          <div class="mechanic-step mechanic-outputs">
            <h2 class="section-label">You get back</h2>
            <ul class="artefact-list">
              <For each={OUTPUTS}>
                {(output) => (
                  <li class="artefact">
                    <Icon name={output.icon} />
                    <span class="artefact-name">{output.name}</span>
                  </li>
                )}
              </For>
            </ul>
          </div>

          <div class="mechanic-step mechanic-schedule">
            <h2 class="section-label">You review, a little at a time</h2>
            <Meter
              leadingLabel="12 due today"
              trailingLabel="43 scheduled later"
              done={12}
              total={55}
            />
            <p class="mechanic-note">
              Each item comes back just before you would have forgotten it, so
              most days are short.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
