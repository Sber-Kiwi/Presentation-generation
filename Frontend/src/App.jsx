import { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar";
import StartChat from "./components/StartChat";
import MainContent from "./components/MainContent";
import BlockingLoader from "./components/BlockingLoader";
import Notification from "./components/Notification";
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

  // Ссылка на текущий экземпляр MainContent — через неё дёргаем отправку
  // накопленных drag-and-drop изменений (см. flushMainContentChanges ниже).
  const mainContentRef = useRef(null);

  const currentSlidesRef = useRef(currentSlides);
  useEffect(() => {
    currentSlidesRef.current = currentSlides;
  }, [currentSlides]);

  const [blocking, setBlocking] = useState({ active: false, messages: [] });

  const [startChatError, setStartChatError] = useState(null);
  const [saveError, setSaveError] = useState(null);

  const [notice, setNotice] = useState(null);
  const notify = (text, type = "info") =>
    setNotice({ text, type, key: Date.now() });

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

  async function flushMainContentChanges() {
    try {
      await mainContentRef.current?.flushPendingChanges();
    } catch (_err) {
      // Ошибки по отдельным слайдам уже показаны пользователю через notify
      // внутри MainContent — здесь дальше можно спокойно продолжать
      // (сохранение/переход не должны намертво блокироваться).
    }
  }

  async function handleSelectChat(newChatId) {
    if (blocking.active || newChatId === selectedChatId) return;

    if (selectedChatId !== "new" && currentSlides.length > 0) {
      await flushMainContentChanges();
      setSlidesCache((prev) => ({
        ...prev,
        [selectedChatId]: currentSlidesRef.current,
      }));
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

  async function handleSave() {
    if (selectedChatId === "new" || currentSlides.length === 0) return;

    const includedSlides = currentSlides.filter((s) => s.state.inPresentation);
    if (includedSlides.length === 0) {
      notify("Вы не можете сохранить пустую презентацию.", "error");
      return;
    }

    setSaveError(null);
    await flushMainContentChanges();

    const freshSlides = currentSlidesRef.current;

    const slideStates = freshSlides.map((s) => ({
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
      notify("Презентация успешно загружена на устройство.", "success");
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
            ref={mainContentRef}
            chatId={selectedChatId}
            chatTitle={currentChat?.title}
            slides={currentSlides}
            setSlides={setCurrentSlides}
            onSave={handleSave}
            globalBusy={blocking.active}
            notify={notify}
          />
        )
      )}

      {saveError && <p className="error-text global-error">{saveError}</p>}

      {blocking.active && <BlockingLoader messages={blocking.messages} />}
      <Notification notice={notice} onClose={() => setNotice(null)} />
    </>
  );
}
