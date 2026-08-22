import { FlashcardWording } from "./flashcard-wording";
import { MnemonicPrompt } from "./mnemonic-prompt";
import type { Flashcard } from "./flashcard-models";

type MnemonicAsk = {
  readonly question: string;
  readonly shownAs: string;
};

export const MnemonicRequest = {
  forCard(card: Flashcard): MnemonicAsk {
    const asked = FlashcardWording.of(card.face);

    return {
      question: MnemonicPrompt.forCard(asked.question, asked.answer),
      shownAs: MnemonicPrompt.shownFor(asked.question),
    };
  },
};
