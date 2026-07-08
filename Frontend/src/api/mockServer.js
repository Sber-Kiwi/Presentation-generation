// Мок-реализация бэкенда из backend.yaml. Имитирует асинхронные задачи
// (генерация / правка / экспорт) через очередь pending -> processing -> done.
// Как только появится настоящий сервер — просто переключите
// USE_MOCK_API в api/config.js на false, менять компоненты не потребуется.
import { ApiError } from "./errors";
import {
  db,
  findChat,
  findSlide,
  nextId,
  buildFakeChat,
  buildEditedVersion,
} from "./mockData";
import { sleep } from "./poll";

// taskID -> { kind, status, result, error }
const tasks = new Map();

function createTask(kind, run) {
  const taskID = nextId("task");
  tasks.set(taskID, { kind, status: "pending", result: null, error: null });

  (async () => {
    await sleep(900);
    const pendingTask = tasks.get(taskID);
    if (pendingTask) pendingTask.status = "processing";

    await sleep(1800);
    const task = tasks.get(taskID);
    if (!task) return;
    try {
      const result = await run();
      task.status = "done";
      task.result = result;
    } catch (err) {
      task.status = "failed";
      task.error = err.message || "Неизвестная ошибка";
    }
  })();

  return taskID;
}

// GET /chats/{chatID}/downloads/status не принимает taskID в пути, поэтому
// для него храним "последнюю" задачу экспорта отдельно, по chatID.
const latestDownloadTask = new Map();
const downloadBlobs = new Map();

export const mockApi = {
  async listChats() {
    await sleep(500);
    return db.chats.map((c) => ({ chatID: c.id, title: c.title }));
  },

  async createChat({ prompt, file }) {
    await sleep(400);
    if (!prompt || !prompt.trim()) {
      throw new ApiError("Введите текст запроса", {
        status: 422,
        code: "VALIDATION_ERROR",
      });
    }
    if (!file) {
      throw new ApiError("Прикрепите .csv файл с данными", {
        status: 422,
        code: "VALIDATION_ERROR",
      });
    }

    const chatId = nextId("chat");
    const taskID = createTask("generate", () => {
      const chat = buildFakeChat(prompt, file.name);
      chat.id = chatId;
      db.chats.push(chat);
      return { chatId };
    });

    return { chatID: chatId, taskID };
  },

  async getChatStatus(chatId, taskId) {
    await sleep(200);
    const task = tasks.get(taskId);
    if (!task) {
      throw new ApiError("Задача не найдена", {
        status: 404,
        code: "NOT_FOUND",
      });
    }
    return { status: task.status, error: task.error ?? null };
  },

  async getChat(chatId) {
    await sleep(350);
    const chat = findChat(chatId);
    if (!chat) {
      throw new ApiError("Чат не найден", { status: 404, code: "NOT_FOUND" });
    }
    return JSON.parse(JSON.stringify(chat));
  },

  async createSlideEdit(chatId, slideId, { prompt, versionID }) {
    await sleep(300);
    const slide = findSlide(chatId, slideId);
    if (!slide) {
      throw new ApiError("Слайд не найден", {
        status: 404,
        code: "NOT_FOUND",
      });
    }
    if (!prompt || !prompt.trim()) {
      throw new ApiError("Введите текст правки", {
        status: 422,
        code: "VALIDATION_ERROR",
      });
    }
    const baseVersion = slide.versions.find((v) => v.versionID === versionID);
    if (!baseVersion) {
      throw new ApiError("Версия слайда не найдена", {
        status: 422,
        code: "VALIDATION_ERROR",
      });
    }

    const taskID = createTask("slide_edit", () => {
      const newVersion = buildEditedVersion(baseVersion, prompt);
      slide.versions.push(newVersion);
      return { newVersionID: newVersion.versionID };
    });

    return { chatID: chatId, taskID };
  },

  async getSlideEditStatus(chatId, slideId, taskId) {
    await sleep(200);
    const task = tasks.get(taskId);
    if (!task) {
      throw new ApiError("Задача не найдена", {
        status: 404,
        code: "NOT_FOUND",
      });
    }
    return {
      status: task.status,
      newVersionID: task.result?.newVersionID ?? null,
      error: task.error ?? null,
    };
  },

  async getSlide(chatId, slideId, versionID) {
    await sleep(250);
    const slide = findSlide(chatId, slideId);
    if (!slide) {
      throw new ApiError("Слайд не найден", {
        status: 404,
        code: "NOT_FOUND",
      });
    }
    const version = versionID
      ? slide.versions.find((v) => v.versionID === versionID)
      : slide.versions.find((v) => v.versionID === slide.state.selectedVersionID);
    if (!version) {
      throw new ApiError("Версия слайда не найдена", {
        status: 404,
        code: "NOT_FOUND",
      });
    }
    return { ...JSON.parse(JSON.stringify(version)), slideID: slideId };
  },

  // Drag-and-drop на фронте пока не реализован — это заглушка, которая
  // просто "принимает" версию слайда, ничего не делая на сервере.
  async createSlideVersion(chatId, slideId, versionPayload) {
    await sleep(200);
    console.log(
      "[mock] createSlideVersion (drag-and-drop) — заглушка:",
      chatId,
      slideId,
      versionPayload,
    );
    return { chatID: chatId, taskID: null };
  },

  async createDownload(chatId, slideStates) {
    await sleep(300);
    const chat = findChat(chatId);
    if (!chat) {
      throw new ApiError("Чат не найден", { status: 404, code: "NOT_FOUND" });
    }
    if (!Array.isArray(slideStates) || slideStates.length === 0) {
      throw new ApiError("Список слайдов для экспорта пуст", {
        status: 422,
        code: "VALIDATION_ERROR",
      });
    }

    const taskID = createTask("download", () => {
      // Настоящий бэкенд соберёт тут pptx + json и упакует в zip.
      const payload = JSON.stringify({ chatId, slideStates }, null, 2);
      const blob = new Blob([payload], { type: "application/zip" });
      downloadBlobs.set(chatId, blob);
      return { ready: true };
    });
    latestDownloadTask.set(chatId, taskID);

    return { chatID: chatId, taskID };
  },

  async getDownloadStatus(chatId) {
    await sleep(200);
    const taskID = latestDownloadTask.get(chatId);
    if (!taskID) {
      throw new ApiError("Экспорт для этого чата ещё не запускался", {
        status: 404,
        code: "NOT_FOUND",
      });
    }
    const task = tasks.get(taskID);
    if (!task) {
      throw new ApiError("Задача не найдена", {
        status: 404,
        code: "NOT_FOUND",
      });
    }
    return { status: task.status, error: task.error ?? null };
  },

  async downloadFile(chatId) {
    await sleep(200);
    const blob = downloadBlobs.get(chatId);
    if (!blob) {
      throw new ApiError("Файл ещё не готов", {
        status: 409,
        code: "NOT_READY",
      });
    }
    return { blob, filename: `presentation_${chatId}.zip` };
  },
};
