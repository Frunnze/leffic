import { HttpClient } from "../../shared/api/http";

export class FilesApi {
  static async openableUrl(fileId: string, extension: string): Promise<string> {
    const query = new URLSearchParams({
      file_id: fileId,
      file_extension: extension,
    }).toString();
    const fileContents = await HttpClient.blob({
      endpoint: `/api/files/file?${query}`,
      headers: { Accept: "application/pdf" },
    });

    return URL.createObjectURL(fileContents);
  }
}
