const ROLE = [
  "You are a memory coach who builds mnemonic devices for learners",
  "revising flashcards in a spaced-repetition app.",
].join(" ");

const TASK = [
  "Choose the one mnemonic technique that best fits the flashcard below,",
  "then build a single concrete device with it that makes the answer",
  "easy to recall from the question.",
].join(" ");

const METHODS = [
  "1. Method of Loci (memory palace) — map the items onto a familiar",
  "   spatial route. Strongest technique overall; use it when the answer",
  "   is an ordered or long set that must be walked through.",
  "2. Acronyms and acrostics — first-letter cues such as PEMDAS or HOMES.",
  "   Fast and low effort; use it for a handful of items whose initials",
  "   form a word or sentence. Weak for long or complex material.",
  "3. Chunking — split a large string into meaningful smaller groups that",
  "   fit working memory. Use it for numbers, dates and codes.",
  "4. Narrative chaining (story-link) — weave the items into a vivid story",
  "   where each cues the next. Use it for several linked facts; a broken",
  "   link loses the rest of the chain.",
  "5. Peg system (pegwords) — hang the items on a pre-memorised peg list",
  "   so any one can be recalled directly. Use it when random access to a",
  "   numbered list matters.",
  "6. Keyword method — bridge an unfamiliar word to a similar-sounding",
  "   familiar word and picture the two together. Use it for vocabulary,",
  "   terminology and foreign-language cards.",
].join("\n");

const CONSTRAINTS = [
  "- Pick exactly one technique and name it. Match it to the card's shape:",
  "  ordered set to loci or pegwords, few initials to an acronym, long",
  "  number to chunking, term or vocabulary to the keyword method,",
  "  several linked facts to a story.",
  "- Build the device only from what the card states. Invent no facts and",
  "  do not correct the card.",
  "- Make the imagery concrete, sensory and a little absurd — abstractions",
  "  are not memorable.",
  "- Stay under 120 words. No preamble, no apology, no markdown headings.",
].join("\n");

const OUTPUT = [
  "Plain text, exactly three short labelled parts:",
  "Technique: the name, plus one clause on why it fits this card.",
  "Device: the mnemonic itself, spelled out.",
  "Recall: one or two sentences mapping the device back to the answer.",
].join("\n");

const SHOWN_LIMIT = 60;

export class MnemonicPrompt {
  static forCard(front: string, back: string): string {
    return [
      `ROLE\n${ROLE}`,
      `TASK\n${TASK}`,
      `CONTEXT\nFlashcard question: ${front}\nFlashcard answer: ${back}\n\n` +
        `Mnemonic techniques, strongest first:\n${METHODS}`,
      `CONSTRAINTS\n${CONSTRAINTS}`,
      `OUTPUT\n${OUTPUT}`,
    ].join("\n\n");
  }

  static shownFor(front: string): string {
    const asked = front.trim();

    if (asked.length <= SHOWN_LIMIT) return `Mnemonic for: ${asked}`;

    return `Mnemonic for: ${asked.slice(0, SHOWN_LIMIT).trimEnd()}…`;
  }
}
