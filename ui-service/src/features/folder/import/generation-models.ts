export type TaskStatus = "PENDING" | "SUCCESS" | "FAILURE";

export type GenerationSource =
  | {
      readonly kind: "file";
      readonly fileId: string;
      readonly extension: string;
      readonly firstPage: number | null;
      readonly lastPage: number | null;
    }
  | { readonly kind: "link"; readonly url: string }
  | { readonly kind: "topic"; readonly topic: string };

export type GenerationOrigin = {
  readonly kind: "file" | "link" | "topic" | "text";
  readonly reference: string;
};

export type GenerationTaskIds = {
  readonly flashcardsTaskIds: readonly string[];
  readonly noteTaskId: string | null;
  readonly testTaskIds: readonly string[];
};

export type UploadedFile = {
  readonly fileId: string;
  readonly name: string;
  readonly extension: string;
  readonly createdAt: string;
};
