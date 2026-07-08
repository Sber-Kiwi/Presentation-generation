import { USE_MOCK_API } from "./config";
import { mockApi } from "./mockServer";
import { realApi } from "./realClient";

// Единая точка входа: компоненты импортируют `api` отсюда и не знают,
// мок это или настоящий бэкенд.
export const api = USE_MOCK_API ? mockApi : realApi;

export { ApiError } from "./errors";
export { pollUntilTerminal } from "./poll";
export { POLL_INTERVAL_MS } from "./config";

// Скачивает Blob как файл в браузере (для GET /chats/{chatID}/downloads).
export function saveBlobAsFile(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
