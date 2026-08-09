export type Note = {
  readonly name: string;
  readonly content: string;
  readonly readingMinutes: number | null;
  readonly isRead: boolean;
};
