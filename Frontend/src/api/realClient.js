// Настоящий клиент к бэкенду, описанному в backend.yaml.
// Используется, когда USE_MOCK_API === false (см. api/config.js).
import { API_BASE_URL } from "./config";
import { ApiError } from "./errors";

async function safeFetch(url, options) {
  try {
    return await fetch(url, options);
  } catch (_err) {
    throw new ApiError("Соединение с сервером потеряно.", {
      status: 0,
      code: "NETWORK_ERROR",
    });
  }
}

async function handleResponse(res, { binary = false } = {}) {
  if (res.ok) {
    if (binary) {
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition") || "";
      const match = disposition.match(/filename="?([^"]+)"?/i);
      return { blob, filename: match ? match[1] : "presentation.zip" };
    }
    if (res.status === 204) return null;
    return res.json();
  }

  let payload = null;
  try {
    payload = await res.json();
  } catch (_err) {
    // тело ответа не JSON — оставляем payload как есть
  }
  const fallback =
    res.status >= 500
      ? "Внутренняя ошибка системы. Повторите запрос."
      : `Ошибка запроса (${res.status})`;
  let errorMessage = payload?.message || fallback;
  if (payload?.status === "VALIDATION_ERROR" && Array.isArray(payload?.details) && payload.details.length > 0) {
    errorMessage = payload.details.map((d) => d.message).join(", ");
  }

  throw new ApiError(errorMessage, {
    status: res.status,
    code: payload?.status || payload?.code,
    details: payload?.details,
  });
}

export const realApi = {
  async listChats() {
    const res = await fetch(`${API_BASE_URL}/chats`);
    return handleResponse(res);
  },

  async createChat({ prompt, file }) {
    const form = new FormData();
    form.append("prompt", prompt);
    form.append("table", file);
    const res = await fetch(`${API_BASE_URL}/chats`, {
      method: "POST",
      body: form,
    });
    return handleResponse(res);
  },

  async getChatStatus(chatId, taskId) {
    const res = await fetch(`${API_BASE_URL}/chats/${chatId}/status/${taskId}`);
    return handleResponse(res);
  },

  async getChat(chatId) {
    const res = await fetch(`${API_BASE_URL}/chats/${chatId}`);
    return handleResponse(res);
  },

  async createSlideEdit(chatId, slideId, { prompt, versionID }) {
    const res = await fetch(
      `${API_BASE_URL}/chats/${chatId}/slides/${slideId}/edits`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, versionID }),
      },
    );
    return handleResponse(res);
  },

  async getSlideEditStatus(chatId, slideId, taskId) {
    const res = await fetch(
      `${API_BASE_URL}/chats/${chatId}/slides/${slideId}/status/${taskId}`,
    );
    return handleResponse(res);
  },

  async getSlide(chatId, slideId, versionID) {
    const url = new URL(`${API_BASE_URL}/chats/${chatId}/slides/${slideId}`, window.location.origin);
    if (versionID) url.searchParams.set("versionID", versionID);
    const res = await fetch(url);
    return handleResponse(res);
  },

  async createSlideVersion(chatId, slideId, versionPayload) {
    const res = await fetch(
      `${API_BASE_URL}/chats/${chatId}/slides/${slideId}/versions`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(versionPayload),
      },
    );
    return handleResponse(res);
  },

  async createDownload(chatId, slideStates) {
    const res = await fetch(`${API_BASE_URL}/chats/${chatId}/downloads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slides: slideStates }),
    });
    return handleResponse(res);
  },

  async getDownloadStatus(chatId) {
    const res = await fetch(`${API_BASE_URL}/chats/${chatId}/downloads/status`);
    return handleResponse(res);
  },

  async downloadFile(chatId) {
    const res = await fetch(`${API_BASE_URL}/chats/${chatId}/downloads`);
    return handleResponse(res, { binary: true });
  },
};
