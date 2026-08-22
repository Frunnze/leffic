import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import fc from "fast-check";
import { AuthApi } from "../src/features/authentication/authentication-api";
import { AuthAside } from "../src/features/authentication/AuthAside";
import { AuthCardHead } from "../src/features/authentication/AuthCardHead";
import { AuthField } from "../src/features/authentication/AuthField";
import LoginPage from "../src/features/authentication/LoginPage";
import { renderAt } from "./router-support";
import { STRONG_PASSWORD, typeInto } from "./authentication-views-support";

describe("AuthAside", () => {
  it("lists every selling point it was given", () => {
    fc.assert(
      fc.property(
        fc.array(fc.stringMatching(/^[A-Za-z ]{1,20}$/), { maxLength: 4 }),
        (points) => {
          const { unmount } = renderAt("/login", "/login", () => (
            <AuthAside heading="Welcome" points={points} />
          ));

          expect(document.querySelectorAll(".auth-points li")).toHaveLength(
            points.length,
          );
          unmount();
        },
      ),
    );
  });

  it("shows the heading it was given", () => {
    renderAt("/login", "/login", () => (
      <AuthAside heading="Everything is waiting" points={[]} />
    ));

    expect(
      screen.getByRole("heading", { name: "Everything is waiting" }),
    ).toBeTruthy();
  });
});

describe("AuthCardHead", () => {
  it("shows the title and subtitle it was given", () => {
    renderAt("/login", "/login", () => (
      <AuthCardHead title="Log in" subtitle="Pick up where you left off." />
    ));

    expect(screen.getByRole("heading", { name: "Log in" })).toBeTruthy();
    expect(document.querySelector(".auth-subtitle")?.textContent).toBe(
      "Pick up where you left off.",
    );
  });
});

describe("AuthField", () => {
  it("reports whatever is typed into it", () => {
    fc.assert(
      fc.property(fc.stringMatching(/^[A-Za-z]{1,10}$/), (typed) => {
        const onInput = vi.fn();
        const { unmount } = renderAt("/login", "/login", () => (
          <AuthField
            id="email"
            label="Email"
            type="email"
            autocomplete="email"
            value=""
            error=""
            onInput={onInput}
          />
        ));

        typeInto("Email", typed);

        expect(onInput).toHaveBeenCalledWith(typed);
        unmount();
      }),
    );
  });

  it("stays quiet while the field is valid", () => {
    renderAt("/login", "/login", () => (
      <AuthField
        id="email"
        label="Email"
        type="email"
        autocomplete="email"
        value=""
        error=""
        onInput={vi.fn()}
      />
    ));
    const field = screen.getByLabelText("Email");

    expect(document.querySelector(".field-error")).toBeNull();
    expect(field.getAttribute("aria-invalid")).toBe("false");
    expect(field.getAttribute("aria-describedby")).toBeNull();
  });

  it("shows and points at the error the field carries", () => {
    renderAt("/login", "/login", () => (
      <AuthField
        id="email"
        label="Email"
        type="email"
        autocomplete="email"
        value=""
        error="Enter your email."
        onInput={vi.fn()}
      />
    ));
    const field = screen.getByLabelText("Email");

    expect(document.querySelector(".field-error")?.textContent).toContain(
      "Enter your email.",
    );
    expect(field.getAttribute("aria-invalid")).toBe("true");
    expect(field.getAttribute("aria-describedby")).toBe("email-error");
  });
});

describe("LoginPage", () => {
  it("refuses to submit an empty form", async () => {
    const logIn = vi.spyOn(AuthApi, "logIn");
    renderAt("/login", "/login", () => <LoginPage />);

    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.querySelector(".auth-alert")?.textContent).toContain(
        "Enter your email and password",
      ),
    );
    expect(logIn).not.toHaveBeenCalled();
  });

  it("shows why the gateway refused the credentials", async () => {
    vi.spyOn(AuthApi, "logIn").mockResolvedValue({
      ok: false,
      field: "form",
      message: "That email and password don't match.",
    });
    renderAt("/login", "/login", () => <LoginPage />);

    typeInto("Email", "learner@example.test");
    typeInto("Password", STRONG_PASSWORD);
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.querySelector(".auth-alert")?.textContent).toContain(
        "don't match",
      ),
    );
  });

  it("leaves for the home folder once the login is accepted", async () => {
    vi.spyOn(AuthApi, "logIn").mockResolvedValue({ ok: true });
    const { history } = renderAt("/login", "/login", () => <LoginPage />);

    typeInto("Email", "learner@example.test");
    typeInto("Password", STRONG_PASSWORD);
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() => expect(history.get()).toBe("/folder/home"));
  });

  it("says it is working while the login is in flight", async () => {
    vi.spyOn(AuthApi, "logIn").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderAt("/login", "/login", () => <LoginPage />);

    typeInto("Email", "learner@example.test");
    typeInto("Password", STRONG_PASSWORD);
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Logging in…" }),
      ).toHaveProperty("disabled", true),
    );
  });
});
