import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import StartChat from "./components/StartChat";
import MainContent from "./components/MainContent";
import BlockingLoader from "./components/BlockingLoader";
import {
  api,
  pollUntilTerminal,
  POLL_INTERVAL_MS,
  saveBlobAsFile,
} from "./api";

const NEW_CHAT = { id: "new" };

export default function App() {
  const [isOpen, setIsOpen] = useState(true);

  const [chats, setChats] = useState([NEW_CHAT]);
  const [chatsLoading, setChatsLoading] = useState(true);
  const [chatsError, setChatsError] = useState(null);

  const [selectedChatId, setSelectedChatId] = useState("new");
  const [currentSlides, setCurrentSlides] = useState([]);
  const [slidesCache, setSlidesCache] = useState({});
  const [loadingChatSlides, setLoadingChatSlides] = useState(false);
  const [chatLoadError, setChatLoadError] = useState(null);

  // Единый "блокирующий" оверлей на весь экран: используется и для
  // генерации презентации, и для экспорта (по требованиям задания это
  // один и тот же вид загрузки).
  const [blocking, setBlocking] = useState({ active: false, messages: [] });

  const [startChatError, setStartChatError] = useState(null);
  const [saveError, setSaveError] = useState(null);

  // 1. GET /chats при запуске приложения — пока список не загружен,
  // крутим загрузку на весь экран.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      setChatsLoading(true);
      setChatsError(null);
      try {
        const list = await api.listChats();
        if (cancelled) return;
        const mapped = list.map((c) => ({ id: c.chatID, title: c.title })); //?
        setChats([NEW_CHAT, ...mapped]);
      } catch (err) {
        if (cancelled) return;
        setChatsError(err.message || "Не удалось загрузить список чатов");
        setChats([NEW_CHAT]);
      } finally {
        if (!cancelled) setChatsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Заглушка для будущего drag-and-drop: перед сохранением презентации и
  // перед сменой чата нужно будет отправить накопленные изменения позиций
  // объектов на слайдах через POST /chats/{chatID}/slides/{slideID}/versions.
  async function flushPendingDragChanges(chatId, slides) {
    void chatId;
    void slides;
    // TODO: когда появится drag-and-drop, пройтись по слайдам с
    // несохранёнными изменениями расположения объектов и вызвать
    // api.createSlideVersion(chatId, slideId, versionPayload) для каждого.
  }

  // 4. Клик по чату в сайдбаре — подгружаем информацию о чате (или берём
  // из кэша, если уже открывали его в этой сессии).
  async function handleSelectChat(newChatId) {
    if (blocking.active || newChatId === selectedChatId) return;

    if (selectedChatId !== "new" && currentSlides.length > 0) {
      setSlidesCache((prev) => ({ ...prev, [selectedChatId]: currentSlides }));
      await flushPendingDragChanges(selectedChatId, currentSlides);
    }

    setSelectedChatId(newChatId);
    setChatLoadError(null);

    if (newChatId === "new") {
      setCurrentSlides([]);
      return;
    }

    const cached = slidesCache[newChatId];
    if (cached) {
      setCurrentSlides(cached);
      return;
    }

    setLoadingChatSlides(true);
    try {
      const chat = await api.getChat(newChatId);
      setCurrentSlides(chat.slides);
      setChats((prev) =>
        prev.map((c) => (c.id === newChatId ? { ...c, title: chat.title } : c)),
      );
    } catch (err) {
      setChatLoadError(err.message || "Не удалось загрузить чат");
      setCurrentSlides([]);
    } finally {
      setLoadingChatSlides(false);
    }
  }

  // 2. Отправка стартового запроса: POST /chats -> ждём статус ->
  // GET /chats/{chatID} и открываем готовый чат.
  async function handleCreateChat(prompt, file) {
    setStartChatError(null);
    try {
      const { chatID, taskID } = await api.createChat({ prompt, file });

      setBlocking({
        active: true,
        messages: [
          "Отправляем запрос на сервер...",
          "Анализируем таблицу...",
          "Генерируем слайды...",
        ],
      });

      const finalStatus = await pollUntilTerminal(
        () => api.getChatStatus(chatID, taskID),
        { intervalMs: POLL_INTERVAL_MS },
      );

      if (finalStatus.status === "failed") {
        throw new Error(
          finalStatus.error || "Не удалось сгенерировать презентацию",
        );
      }

      const chat = await api.getChat(chatID);

      setChats((prev) => {
        const withoutDup = prev.filter((c) => c.id !== chatID);
        const newIdx = withoutDup.findIndex((c) => c.id === "new");
        const next = [...withoutDup];
        next.splice(newIdx + 1, 0, { id: chatID, title: chat.title });
        return next;
      });
      setCurrentSlides(chat.slides);
      setSelectedChatId(chatID);
    } catch (err) {
      setStartChatError(err.message || "Не удалось создать презентацию");
    } finally {
      setBlocking({ active: false, messages: [] });
    }
  }

  // 8-10. Сохранение презентации: POST /downloads -> ждём статус ->
  // GET /downloads (скачиваем zip).
  async function handleSave() {
    if (selectedChatId === "new" || currentSlides.length === 0) return;

    setSaveError(null);
    await flushPendingDragChanges(selectedChatId, currentSlides);

    // В backend.yaml SlideState не содержит slideID (недоработка спеки) —
    // добавляем его сами, чтобы бэкенд понимал, к какому слайду относится
    // каждый статус.
    const slideStates = currentSlides.map((s) => ({
      slideID: s.slideID,
      selectedVersionID: s.state.selectedVersionID,
      inPresentation: s.state.inPresentation,
    }));

    try {
      await api.createDownload(selectedChatId, slideStates);

      setBlocking({
        active: true,
        messages: [
          "Собираем презентацию...",
          "Формируем PPTX...",
          "Почти готово...",
        ],
      });

      // Обратите внимание: GET .../downloads/status не принимает  в
      // пути (см. backend.yaml), поэтому опрашиваем именно по chatID.taskID
      const finalStatus = await pollUntilTerminal(
        () => api.getDownloadStatus(selectedChatId),
        { intervalMs: POLL_INTERVAL_MS },
      );

      if (finalStatus.status === "failed") {
        throw new Error(
          finalStatus.error || "Не удалось подготовить файл для скачивания",
        );
      }

      const { blob, filename } = await api.downloadFile(selectedChatId);
      saveBlobAsFile(blob, filename);
    } catch (err) {
      setSaveError(err.message || "Не удалось сохранить презентацию");
    } finally {
      setBlocking({ active: false, messages: [] });
    }
  }

  const currentChat = chats.find((chat) => chat.id === selectedChatId);
  const arrowSymbol = isOpen ? "<" : ">";
  const symbolsArray = Array(50).fill(arrowSymbol);

  const toggleChats = () => {
    setIsOpen(!isOpen);
  };

  // 1. Пока GET /chats не завершился — крутим загрузку на весь экран.
  if (chatsLoading) {
    return <BlockingLoader messages={["Загружаем историю чатов..."]} />;
  }

  return (
    <>
      <Sidebar
        isOpen={isOpen}
        chats={chats}
        selectedChatId={selectedChatId}
        onSelectChat={handleSelectChat}
      />
      <button id="toggle-chats" className="toggle-chats" onClick={toggleChats}>
        <span className="symbol-chain">
          {symbolsArray.map((symbol, index) => (
            <span key={index}>{symbol}</span>
          ))}
        </span>
      </button>

      {chatsError && <p className="error-text global-error">{chatsError}</p>}

      {selectedChatId === "new" ? (
        <StartChat
          onSubmit={handleCreateChat}
          disabled={blocking.active}
          error={startChatError}
        />
      ) : loadingChatSlides ? (
        <div className="main-loading">Загружаем чат...</div>
      ) : chatLoadError ? (
        <div className="main-loading error-text">{chatLoadError}</div>
      ) : (
        currentSlides.length > 0 && (
          <MainContent
            key={selectedChatId}
            chatId={selectedChatId}
            chatTitle={currentChat?.title}
            slides={currentSlides}
            setSlides={setCurrentSlides}
            onSave={handleSave}
            globalBusy={blocking.active}
          />
        )
      )}

      {saveError && <p className="error-text global-error">{saveError}</p>}

      {/* 3, 9. Полноэкранная загрузка на время генерации чата / экспорта. */}
      {blocking.active && <BlockingLoader messages={blocking.messages} />}
    </>
  );
}
