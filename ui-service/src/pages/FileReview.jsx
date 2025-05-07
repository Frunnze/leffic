import { createResource, Show } from "solid-js";
import { useParams } from "@solidjs/router";
import { apiRequest } from "../utils/apiRequest";
import LeftNavBar from "../components/LeftNavBar";

const getFile = async (fileId) => {
  // Fetch the PDF file from the API
  const res = await apiRequest({
    endpoint: `/api/files/file?file_id=${fileId}`,
    headers: {
      Accept: "application/pdf",
    },
  });

  // Convert the response to a Blob (binary data)
  const blob = await res.blob();

  // Create an Object URL from the Blob
  const pdfUrl = URL.createObjectURL(blob);

  return { url: pdfUrl };  // Return the Object URL
};

export default function FileViewer() {
  const params = useParams();
  const [file] = createResource(() => params.id, getFile);

  return (
    <div class="pl-17 h-screen w-screen flex justify-center items-center bg-secondary/10">
        <LeftNavBar/>
        <Show when={file()}>
            <iframe
                src={file().url}
                class="w-screen h-screen border shadow-md"
                type="application/pdf"
            />
        </Show>
    </div>
  );
}