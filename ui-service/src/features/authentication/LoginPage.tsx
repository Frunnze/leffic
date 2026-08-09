import { Show, createSignal, type JSX } from "solid-js";
import { A, useNavigate } from "@solidjs/router";
import { AuthApi } from "./authentication-api";
import { AuthAside } from "./AuthAside";
import { Icon } from "../../shared/ui/icons/Icon";

const HOME_ROUTE = "/folder/home";

const ASIDE_POINTS: readonly string[] = [
  "Today's cards are already scheduled",
  "Your notes and tests stay in sync",
  "Pick up on any device",
];

export default function Login(): JSX.Element {
  const navigate = useNavigate();
  const [email, setEmail] = createSignal("");
  const [password, setPassword] = createSignal("");
  const [error, setError] = createSignal("");
  const [isSubmitting, setSubmitting] = createSignal(false);

  const logIn = async (event: Event): Promise<void> => {
    event.preventDefault();

    if (email().length === 0 || password().length === 0) {
      setError("Enter your email and password to continue.");
      return;
    }

    setSubmitting(true);
    const outcome = await AuthApi.logIn({
      email: email(),
      password: password(),
    });
    setSubmitting(false);

    if (!outcome.ok) {
      setError(outcome.message);
      return;
    }

    navigate(HOME_ROUTE);
  };

  return (
    <div class="screen">
      <div class="auth">
        <AuthAside
          heading="Everything you imported is waiting."
          points={ASIDE_POINTS}
        />

        <div class="auth-main">
          <form class="auth-card" onSubmit={(event) => void logIn(event)}>
            <span class="auth-mark">
              <Icon name="logo" size="lg" />
            </span>

            <div class="auth-head">
              <h1 class="auth-title">Log in</h1>
              <span class="auth-subtitle">Pick up where you left off.</span>
            </div>

            <Show when={error().length > 0}>
              <p class="auth-alert" id="login-error" role="alert">
                <Icon name="failure" size="sm" />
                {error()}
              </p>
            </Show>

            <div class="field">
              <label for="email">Email</label>
              <input
                class="input input-lg"
                id="email"
                type="email"
                autocomplete="email"
                value={email()}
                onInput={(event) => setEmail(event.currentTarget.value)}
              />
            </div>

            <div class="field">
              <div class="field-row">
                <label for="password">Password</label>
                <A class="text-action" href="/login">
                  Reset password
                </A>
              </div>
              <input
                class="input input-lg"
                id="password"
                type="password"
                autocomplete="current-password"
                value={password()}
                onInput={(event) => setPassword(event.currentTarget.value)}
              />
            </div>

            <button
              class="btn btn-primary btn-block btn-lg"
              type="submit"
              disabled={isSubmitting()}
            >
              {isSubmitting() ? "Logging in…" : "Log in"}
            </button>

            <p class="auth-foot">
              New to Leffic? <A class="text-action" href="/sign-up">Create an account</A>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
