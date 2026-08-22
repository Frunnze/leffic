import { describe, expect, it, vi } from "vitest";
import { fireEvent, waitFor } from "@solidjs/testing-library";
import fc from "fast-check";
import { AuthApi } from "../src/features/authentication/authentication-api";
import SignUpPage from "../src/features/authentication/SignUpPage";
import { renderAt } from "./router-support";
import { STRONG_PASSWORD, typeInto } from "./authentication-views-support";

describe("SignUpPage", () => {
  it("refuses a password shorter than eight characters", async () => {
    await fc.assert(
      fc.asyncProperty(fc.stringMatching(/^.{0,7}$/), async (password) => {
        const signUp = vi.spyOn(AuthApi, "signUp");
        const { unmount } = renderAt("/sign-up", "/sign-up", () => (
          <SignUpPage />
        ));

        typeInto("Username", "learner");
        typeInto("Email", "learner@example.test");
        typeInto("Password", password);
        fireEvent.submit(document.querySelector("form") as HTMLFormElement);

        await waitFor(() =>
          expect(document.querySelector(".field-error")?.textContent).toContain(
            "Use at least 8 characters.",
          ),
        );
        expect(signUp).not.toHaveBeenCalled();
        unmount();
      }),
      { numRuns: 5 },
    );
  });

  it("hints at the password length before anything is typed", () => {
    renderAt("/sign-up", "/sign-up", () => <SignUpPage />);

    expect(document.querySelector(".field-hint")?.textContent).toContain(
      "At least 8 characters",
    );
  });

  it("asks for a username and an email that are missing", async () => {
    renderAt("/sign-up", "/sign-up", () => <SignUpPage />);

    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(
        [...document.querySelectorAll(".field-error")].map(
          (e) => e.textContent,
        ),
      ).toEqual([
        expect.stringContaining("Choose a username."),
        expect.stringContaining("Enter your email."),
        expect.stringContaining("Use at least 8 characters."),
      ]),
    );
  });

  it("blames the field the gateway named", async () => {
    vi.spyOn(AuthApi, "signUp").mockResolvedValue({
      ok: false,
      field: "username",
      message: "That username is taken.",
    });
    renderAt("/sign-up", "/sign-up", () => <SignUpPage />);

    typeInto("Username", "learner");
    typeInto("Email", "learner@example.test");
    typeInto("Password", STRONG_PASSWORD);
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.querySelector(".field-error")?.textContent).toContain(
        "That username is taken.",
      ),
    );
  });

  it("shows a form-wide refusal above the fields", async () => {
    vi.spyOn(AuthApi, "signUp").mockResolvedValue({
      ok: false,
      field: "form",
      message: "We couldn't create the account.",
    });
    renderAt("/sign-up", "/sign-up", () => <SignUpPage />);

    typeInto("Username", "learner");
    typeInto("Email", "learner@example.test");
    typeInto("Password", STRONG_PASSWORD);
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.querySelector(".auth-alert")?.textContent).toContain(
        "We couldn't create the account.",
      ),
    );
  });

  it("leaves for the home folder once the account is made", async () => {
    vi.spyOn(AuthApi, "signUp").mockResolvedValue({ ok: true });
    const { history } = renderAt("/sign-up", "/sign-up", () => <SignUpPage />);

    typeInto("Username", "learner");
    typeInto("Email", "learner@example.test");
    typeInto("Password", STRONG_PASSWORD);
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() => expect(history.get()).toBe("/folder/home"));
  });
});
