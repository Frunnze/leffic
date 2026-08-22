import { describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor } from "@solidjs/testing-library";
import { AskProvider } from "../src/shared/chatbot/AskContext";
import { Chatbot } from "../src/shared/chatbot/Chatbot";
import { ChatbotApi } from "../src/shared/chatbot/chatbot-api";
import { renderAt } from "./router-support";
import { AskRaiser } from "./shell-support";

describe("Chatbot", () => {
  function renderChat(onClose = vi.fn()): void {
    renderAt("/folder/home", "/folder/:id", () => (
      <AskProvider>
        <Chatbot onClose={onClose} />
      </AskProvider>
    ));
  }

  function typeMessage(text: string): void {
    fireEvent.input(screen.getByLabelText("Message"), {
      target: { value: text },
    });
  }

  it("says so before anything has been asked", () => {
    renderChat();

    expect(document.querySelector(".chat-empty-title")?.textContent).toBe(
      "No messages yet",
    );
  });

  it("shows the question and then the answer", async () => {
    vi.spyOn(ChatbotApi, "ask").mockResolvedValue("Because of mitosis.");
    renderChat();

    typeMessage("Why?");
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(
        [...document.querySelectorAll(".chat-bubble")].map(
          (b) => b.textContent,
        ),
      ).toEqual(["Why?", "Because of mitosis."]),
    );
  });

  it("says it is thinking while the answer is in flight", async () => {
    vi.spyOn(ChatbotApi, "ask").mockImplementation(
      () => new Promise(() => undefined),
    );
    renderChat();

    typeMessage("Why?");
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.body.textContent).toContain("Thinking…"),
    );
    expect(screen.getByRole("button", { name: "Send" })).toHaveProperty(
      "disabled",
      true,
    );
  });

  it("refuses to send a blank question", () => {
    const asking = vi.spyOn(ChatbotApi, "ask");
    renderChat();

    typeMessage("   ");
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(asking).not.toHaveBeenCalled();
  });

  it("refuses to send while it is still waiting", async () => {
    const asking = vi
      .spyOn(ChatbotApi, "ask")
      .mockImplementation(() => new Promise(() => undefined));
    renderChat();

    typeMessage("Why?");
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);
    await waitFor(() => expect(asking).toHaveBeenCalledTimes(1));

    typeMessage("Again?");
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    expect(asking).toHaveBeenCalledTimes(1);
  });

  it("apologises when the answer cannot be fetched", async () => {
    vi.spyOn(ChatbotApi, "ask").mockRejectedValue(new Error("offline"));
    renderChat();

    typeMessage("Why?");
    fireEvent.submit(document.querySelector("form") as HTMLFormElement);

    await waitFor(() =>
      expect(document.body.textContent).toContain(
        "Something went wrong. Try again.",
      ),
    );
  });

  it("sends on enter but not on shift-enter", async () => {
    const asking = vi.spyOn(ChatbotApi, "ask").mockResolvedValue("ok");
    renderChat();

    typeMessage("Why?");
    fireEvent.keyDown(screen.getByLabelText("Message"), {
      key: "Enter",
      shiftKey: true,
    });

    expect(asking).not.toHaveBeenCalled();

    fireEvent.keyDown(screen.getByLabelText("Message"), { key: "Enter" });

    await waitFor(() => expect(asking).toHaveBeenCalledTimes(1));
  });

  it("ignores every other key", () => {
    const asking = vi.spyOn(ChatbotApi, "ask");
    renderChat();

    typeMessage("Why?");
    fireEvent.keyDown(screen.getByLabelText("Message"), { key: "a" });

    expect(asking).not.toHaveBeenCalled();
  });

  it("asks whatever another page handed it", async () => {
    vi.spyOn(ChatbotApi, "ask").mockResolvedValue("Try a memory palace.");
    renderAt("/folder/home", "/folder/:id", () => (
      <AskProvider>
        <AskRaiser />
        <Chatbot onClose={vi.fn()} />
      </AskProvider>
    ));

    fireEvent.click(screen.getByRole("button", { name: "raise" }));

    await waitFor(() =>
      expect(
        [...document.querySelectorAll(".chat-bubble")].map(
          (b) => b.textContent,
        ),
      ).toEqual(["Mnemonic for: Front", "Try a memory palace."]),
    );
    expect(ChatbotApi.ask).toHaveBeenCalledWith([
      { role: "user", content: "the long prompt" },
    ]);
  });

  it("closes when asked", () => {
    const onClose = vi.fn();
    renderChat(onClose);

    fireEvent.click(screen.getByRole("button", { name: "Close Ask" }));

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
