import { Show, createSignal, type JSX } from "solid-js";
import { A, useNavigate } from "@solidjs/router";
import { AuthApi } from "./authentication-api";
import { AuthAside } from "./AuthAside";
import { AuthCardHead } from "./AuthCardHead";
import { AuthField } from "./AuthField";
import { Icon } from "../../shared/ui/icons/Icon";

const HOME_ROUTE = "/folder/home";
const MINIMUM_PASSWORD_LENGTH = 8;

const ASIDE_POINTS: readonly string[] = [
  "Import a file, link or topic in one step",
  "Flashcards, notes and a test come back",
  "Reviews are scheduled for you",
];

type FieldErrors = {
  readonly username: string;
  readonly email: string;
  readonly password: string;
  readonly form: string;
};

const NO_ERRORS: FieldErrors = { username: "", email: "", password: "", form: "" };

export default function SignUp(): JSX.Element {
  const navigate = useNavigate();
  const [username, setUsername] = createSignal("");
  const [email, setEmail] = createSignal("");
  const [password, setPassword] = createSignal("");
  const [errors, setErrors] = createSignal<FieldErrors>(NO_ERRORS);

  const localErrors = (): FieldErrors => ({
    username: username().length === 0 ? "Choose a username." : "",
    email: email().length === 0 ? "Enter your email." : "",
    password:
      password().length < MINIMUM_PASSWORD_LENGTH
        ? `Use at least ${MINIMUM_PASSWORD_LENGTH} characters.`
        : "",
    form: "",
  });

  const signUp = async (event: Event): Promise<void> => {
    event.preventDefault();
    const found = localErrors();
    setErrors(found);

    if (found.username !== "" || found.email !== "" || found.password !== "") {
      return;
    }

    const outcome = await AuthApi.signUp({
      username: username(),
      email: email(),
      password: password(),
    });

    if (!outcome.ok) {
      setErrors({ ...NO_ERRORS, [outcome.field]: outcome.message });
      return;
    }

    navigate(HOME_ROUTE);
  };

  return (
    <div class="screen">
      <div class="auth">
        <AuthAside heading="One import, a whole study set." points={ASIDE_POINTS} />

        <div class="auth-main">
          <form class="auth-card" onSubmit={(event) => void signUp(event)}>
            <AuthCardHead
              title="Create your account"
              subtitle="Free, and you can import straight away."
            />

            <Show when={errors().form.length > 0}>
              <p class="auth-alert" role="alert">
                <Icon name="failure" size="sm" />
                {errors().form}
              </p>
            </Show>

            <AuthField
              id="username"
              label="Username"
              type="text"
              autocomplete="username"
              value={username()}
              error={errors().username}
              onInput={setUsername}
            />

            <AuthField
              id="email"
              label="Email"
              type="email"
              autocomplete="email"
              value={email()}
              error={errors().email}
              onInput={setEmail}
            />

            <div class="field">
              <label for="password">Password</label>
              <input
                class="input input-lg"
                id="password"
                type="password"
                autocomplete="new-password"
                aria-invalid={errors().password.length > 0}
                aria-describedby="password-hint"
                value={password()}
                onInput={(event) => setPassword(event.currentTarget.value)}
              />
              <Show
                when={errors().password.length > 0}
                fallback={
                  <span class="field-hint" id="password-hint">
                    At least {MINIMUM_PASSWORD_LENGTH} characters.
                  </span>
                }
              >
                <span class="field-error" id="password-hint">
                  <Icon name="failure" size="sm" />
                  {errors().password}
                </span>
              </Show>
            </div>

            <button class="btn btn-primary btn-block btn-lg" type="submit">
              Create account
            </button>

            <p class="auth-foot">
              Already have an account? <A class="text-action" href="/login">Log in</A>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
