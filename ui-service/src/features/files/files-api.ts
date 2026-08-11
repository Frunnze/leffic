import { HttpClient } from "../../shared/api/http";
import { Json } from "../../shared/api/json";

const BOOKMARK_ENDPOINT = "/api/content/file-bookmark";

export type OpenedFile = {
  readonly url: string;
  readonly bookmarkedPage: number | null;
};

export class FilesApi {
  static async opened(
    fileId: string,
    extension: string,
  ): Promise<OpenedFile> {
    const [url, bookmarkedPage] = await Promise.all([
      FilesApi.openableUrl(fileId, extension),
      FilesApi.bookmarkedPage(fileId),
    ]);

    return { url, bookmarkedPage };
  }

  static async openableUrl(fileId: string, extension: string): Promise<string> {
    const query = new URLSearchParams({
      file_id: fileId,
      file_extension: extension,
    }).toString();
    const fileContents = await HttpClient.blob({
      endpoint: `/api/content/file?${query}`,
      headers: { Accept: "application/pdf" },
    });

    return URL.createObjectURL(fileContents);
  }

  static async bookmarkedPage(fileId: string): Promise<number | null> {
    const query = new URLSearchParams({ file_id: fileId }).toString();
    const payload = await HttpClient.json({
      endpoint: `${BOOKMARK_ENDPOINT}?${query}`,
    });

    return Json.numberOrNull(Json.object(payload, "bookmark").page);
  }

  static async rememberPage(
    fileId: string,
    page: number,
  ): Promise<number | null> {
    const payload = await HttpClient.json({
      endpoint: BOOKMARK_ENDPOINT,
      method: "PUT",
      body: { file_id: fileId, page },
    });

    return Json.numberOrNull(Json.object(payload, "bookmark").page);
  }

  static async forgetPage(fileId: string): Promise<void> {
    const query = new URLSearchParams({ file_id: fileId }).toString();
    await HttpClient.json({
      endpoint: `${BOOKMARK_ENDPOINT}?${query}`,
      method: "DELETE",
    });
  }
}
