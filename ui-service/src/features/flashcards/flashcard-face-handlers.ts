import { createComponent, type JSX } from "solid-js";
import { Json, type JsonObject } from "../../shared/api/json";
import {
  BasicAnswer,
  BasicFields,
  BasicPrompt,
  ClozeAnswer,
  ClozeFields,
  ClozePrompt,
  FeynmanAnswer,
  FeynmanFields,
  FeynmanPrompt,
  ListAnswer,
  ListFields,
  ListPrompt,
} from "./flashcard-face-views";
import type { FlashcardFace } from "./flashcard-models";

export type FlashcardWords = {
  readonly question: string;
  readonly answer: string;
};

type FaceKind = FlashcardFace["kind"];
type FaceOf<Kind extends FaceKind> = Extract<FlashcardFace, { kind: Kind }>;

type FaceHandler<Kind extends FaceKind> = {
  readonly fromContent: (content: JsonObject) => FaceOf<Kind>;
  readonly toContent: (
    face: FaceOf<Kind>,
  ) => Readonly<Record<string, unknown>>;
  readonly wording: (face: FaceOf<Kind>) => FlashcardWords;
  readonly fields: (
    face: FaceOf<Kind>,
    onChange: (face: FlashcardFace) => void,
  ) => JSX.Element;
  readonly prompt: (face: FaceOf<Kind>) => JSX.Element;
  readonly answer: (face: FaceOf<Kind>) => JSX.Element;
};

const strings = (raw: unknown): readonly string[] => {
  if (!Array.isArray(raw)) return [];

  return raw
    .filter((entry): entry is string => typeof entry === "string")
    .map((entry) => entry.trim())
    .filter((entry) => entry.length > 0);
};

const HANDLERS = new Map<FaceKind, unknown>();

HANDLERS.set("basic", {
  fromContent: (content) => ({
    kind: "basic",
    front: Json.stringOr(content.front, ""),
    back: Json.stringOr(content.back, ""),
  }),
  toContent: (face) => ({ front: face.front, back: face.back }),
  wording: (face) => ({ question: face.front, answer: face.back }),
  fields: (face, onChange) =>
    createComponent(BasicFields, { face, onChange }),
  prompt: (face) => createComponent(BasicPrompt, { face }),
  answer: (face) => createComponent(BasicAnswer, { face }),
} satisfies FaceHandler<"basic">);

HANDLERS.set("cloze", {
  fromContent: (content) => ({
    kind: "cloze",
    text: Json.stringOr(content.text, ""),
    hiddenParts: strings(content.hidden_parts),
  }),
  toContent: (face) => ({
    text: face.text,
    hidden_parts: [...face.hiddenParts],
  }),
  wording: (face) => ({
    question: face.text,
    answer: `The hidden parts are: ${face.hiddenParts.join(", ")}`,
  }),
  fields: (face, onChange) =>
    createComponent(ClozeFields, { face, onChange }),
  prompt: (face) => createComponent(ClozePrompt, { face }),
  answer: (face) => createComponent(ClozeAnswer, { face }),
} satisfies FaceHandler<"cloze">);

HANDLERS.set("list", {
  fromContent: (content) => ({
    kind: "list",
    question: Json.stringOr(content.question, ""),
    items: strings(content.items),
  }),
  toContent: (face) => ({
    question: face.question,
    items: [...face.items],
  }),
  wording: (face) => ({
    question: face.question,
    answer: face.items.join(", "),
  }),
  fields: (face, onChange) =>
    createComponent(ListFields, { face, onChange }),
  prompt: (face) => createComponent(ListPrompt, { face }),
  answer: (face) => createComponent(ListAnswer, { face }),
} satisfies FaceHandler<"list">);

HANDLERS.set("feynman", {
  fromContent: (content) => ({
    kind: "feynman",
    prompt: Json.stringOr(content.prompt, ""),
    referenceExplanation: Json.stringOr(
      content.reference_explanation,
      "",
    ),
  }),
  toContent: (face) => ({
    prompt: face.prompt,
    reference_explanation: face.referenceExplanation,
  }),
  wording: (face) => ({
    question: face.prompt,
    answer: face.referenceExplanation,
  }),
  fields: (face, onChange) =>
    createComponent(FeynmanFields, { face, onChange }),
  prompt: (face) => createComponent(FeynmanPrompt, { face }),
  answer: (face) => createComponent(FeynmanAnswer, { face }),
} satisfies FaceHandler<"feynman">);

const handlerFor = <Kind extends FaceKind>(
  kind: Kind,
): FaceHandler<Kind> => HANDLERS.get(kind) as FaceHandler<Kind>;

export const FlashcardFaceHandlers = {
  toFace(type: string, content: JsonObject): FlashcardFace {
    if (HANDLERS.has(type as FaceKind)) {
      return handlerFor(type as FaceKind).fromContent(content);
    }

    return handlerFor("basic").fromContent(content);
  },

  toContent(face: FlashcardFace): Readonly<Record<string, unknown>> {
    return handlerFor(face.kind).toContent(face);
  },

  of(face: FlashcardFace): FlashcardWords {
    return handlerFor(face.kind).wording(face);
  },

  fields(
    face: FlashcardFace,
    onChange: (face: FlashcardFace) => void,
  ): JSX.Element {
    return handlerFor(face.kind).fields(face, onChange);
  },

  prompt(face: FlashcardFace): JSX.Element {
    return handlerFor(face.kind).prompt(face);
  },

  answer(face: FlashcardFace): JSX.Element {
    return handlerFor(face.kind).answer(face);
  },
};
