import { HttpClient } from "../../shared/api/http";
import { Json } from "../../shared/api/json";
import type { Note } from "./note-models";

const WORDS_PER_MINUTE = 200;
const TAG_PATTERN = /<[^>]*>/g;
const WHITESPACE_PATTERN = /\s+/;

export class NotesApi {
  static async note(noteId: string): Promise<Note> {
    const query = new URLSearchParams({ note_id: noteId }).toString();
    const payload = await HttpClient.json({
      endpoint: `/api/content/note?${query}`,
    });
    const rawNote = Json.object(payload, "note");
    const content = Json.stringOr(rawNote.content, "");

    return {
      name: Json.stringOr(rawNote.name, "Untitled note"),
      content,
      readingMinutes: NotesApi.readingMinutes(content),
    };
  }

  private static readingMinutes(html: string): number | null {
    const wordCount = html
      .replace(TAG_PATTERN, " ")
      .split(WHITESPACE_PATTERN)
      .filter((word) => word.length > 0).length;

    if (wordCount === 0) return null;

    return Math.max(1, Math.round(wordCount / WORDS_PER_MINUTE));
  }
}
