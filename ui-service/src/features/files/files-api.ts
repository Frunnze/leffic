import type { PDFDocumentProxy } from "pdfjs-dist";
import { HttpClient, UnauthorizedError } from "../../shared/api/http";
import { Session } from "../../shared/api/session";
import { Json } from "../../shared/api/json";
import { PdfViewer } from "./pdf-viewer";

const BOOKMARK_ENDPOINT = "/api/content/file-bookmark";

export type OpenedFile = {
  readonly document: PDFDocumentProxy;
  readonly bookmarkedPage: number | null;
};

export class FilesApi {
  static async opened(
    fileId: string,
    extension: string,
  ): Promise<OpenedFile> {
    const [document, bookmarkedPage] = await Promise.all([
      FilesApi.openedDocument(fileId, extension),
      FilesApi.bookmarkedPage(fileId),
    ]);

    return { document, bookmarkedPage };
  }

  static async openedDocument(
    fileId: string,
    extension: string,
  ): Promise<PDFDocumentProxy> {
    const token = Session.currentToken() ?? (await Session.refresh());

    if (token === null) throw new UnauthorizedError();

    const query = new URLSearchParams({
      file_id: fileId,
      file_extension: extension,
    }).toString();

    return PdfViewer.opened(
      `${Session.baseUrl}/api/content/file?${query}`,
      { Authorization: `Bearer ${token}` },
    );
  }

  static async bookmarkedPage(fileId: string): Promise<number | null> {
    const query = new URLSearchParams({ file_id: fileId }).toString();
    const payload = await HttpClient.json({
      endpoint: `${BOOKMARK_ENDPOINT}?${query}`,
    });

    return Json.optionalNumber(Json.object(payload, "bookmark").page);
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

    return Json.optionalNumber(Json.object(payload, "bookmark").page);
  }

  static async forgetPage(fileId: string): Promise<void> {
    const query = new URLSearchParams({ file_id: fileId }).toString();
    await HttpClient.json({
      endpoint: `${BOOKMARK_ENDPOINT}?${query}`,
      method: "DELETE",
    });
  }
}
