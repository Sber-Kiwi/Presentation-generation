import { useState } from "react";
import Sidebar from "./components/Sidebar";
import StartChat from "./components/StartChat";
import MainContent from "./components/MainContent";
import data from "./json-example.json";

export default function App() {
  const [isOpen, setIsOpen] = useState(true);
  const [chats] = useState(() => {
    const initialChats = data.chats.map((c) => ({ id: c.id, title: c.title }));
    const hasNewChat = initialChats.some((chat) => chat.id === "new");
    if (!hasNewChat) initialChats.unshift({ id: "new" });
    return initialChats;
  });
  const [selectedChatId, setSelectedChatId] = useState("new");

  const [currentSlides, setCurrentSlides] = useState([]);
  const [slidesCache, setSlidesCache] = useState({});

  // Функция для имитации отправки сохраненных изменений на бэкенд
  const saveCurrentDataToBackend = (chatId, slidesData) => {
    if (!chatId || chatId === "new" || slidesData.length === 0) return;
    console.log(`[БЭКЕНД] Сохраняем изменения для чата ${chatId}:`, slidesData);
  };

  // 3. ЕДИНАЯ УМНАЯ ФУНКЦИЯ ПЕРЕКЛЮЧЕНИЯ ЧАТОВ (Вызывается по клику в сайдбаре)
  const handleSelectChat = (newChatId) => {
    // Шаг А: Сохраняем текущие слайды в кэш перед уходом
    if (selectedChatId !== "new" && currentSlides.length > 0) {
      setSlidesCache((prev) => ({ ...prev, [selectedChatId]: currentSlides }));
    }

    // Шаг Б: Имитируем отправку на бэкенд
    saveCurrentDataToBackend(selectedChatId, currentSlides);

    // Шаг В: Меняем выбранный ID
    setSelectedChatId(newChatId);

    // Шаг Г: Загружаем слайды — сначала смотрим в кэш
    if (newChatId === "new") {
      setCurrentSlides([]);
    } else {
      const cached = slidesCache[newChatId];
      if (cached) {
        setCurrentSlides(cached);
      } else {
        const fullChatFromDB = data.chats.find((c) => c.id === newChatId);
        if (fullChatFromDB) {
          setCurrentSlides(JSON.parse(JSON.stringify(fullChatFromDB.slides)));
        }
      }
    }
  };

  const currentChat = chats.find((chat) => chat.id === selectedChatId);
  const arrowSymbol = isOpen ? "<" : ">";
  const symbolsArray = Array(50).fill(arrowSymbol);

  const toggleChats = () => {
    setIsOpen(!isOpen);
  };

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
      {selectedChatId === "new" ? (
        <StartChat />
      ) : (
        currentSlides.length > 0 && (
          <MainContent
            key={selectedChatId}
            chatTitle={currentChat?.title}
            slides={currentSlides}
            setSlides={setCurrentSlides}
            onSave={() =>
              saveCurrentDataToBackend(selectedChatId, currentSlides)
            }
          />
        )
      )}
    </>
  );
}
