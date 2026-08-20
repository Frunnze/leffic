import { createSignal, type Accessor } from "solid-js";

export type PendingAsk = {
  readonly question: string;
  readonly shownAs: string;
};

export type AskStore = {
  readonly isOpen: Accessor<boolean>;
  readonly pendingAsk: Accessor<PendingAsk | null>;
  readonly toggle: () => void;
  readonly close: () => void;
  readonly askAbout: (ask: PendingAsk) => void;
  readonly questionSent: () => void;
};

export class AskStoreFactory {
  static create(): AskStore {
    const [isOpen, setOpen] = createSignal(false);
    const [pendingAsk, setPendingAsk] = createSignal<PendingAsk | null>(null);

    const askAbout = (ask: PendingAsk): void => {
      setPendingAsk(ask);
      setOpen(true);
    };

    return {
      isOpen,
      pendingAsk,
      toggle: () => setOpen(!isOpen()),
      close: () => setOpen(false),
      askAbout,
      questionSent: () => setPendingAsk(null),
    };
  }
}
