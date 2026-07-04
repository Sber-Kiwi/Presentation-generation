import { useState } from "react";
import Sidebar from "./components/Sidebar";
import StartChat from "./components/StartChat";
import MainContent from "./components/MainContent";
import data from "./json-example.json";

export default function App() {
  const [isOpen, setIsOpen] = useState(true);
  const [chats, setChats] = useState(() => {
    const initialChats = data.chats;
    const hasNewChat = initialChats.some((chat) => chat.id === "new");
    if (!hasNewChat) initialChats.unshift({ id: "new" });
    return initialChats;
  });
  const [selectedChatId, setSelectedChatId] = useState("new");

  const toggleChats = () => {
    setIsOpen(!isOpen);
  };

  const currentChat = chats.find((chat) => chat.id === selectedChatId);

  const arrowSymbol = isOpen ? "<" : ">";
  const symbolsArray = Array(50).fill(arrowSymbol);

  return (
    <>
      <Sidebar
        isOpen={isOpen}
        chats={chats}
        selectedChatId={selectedChatId}
        onSelectChat={setSelectedChatId}
      />
      <button id="toggle-chats" className="toggle-chats" onClick={toggleChats}>
        <span className="symbol-chain">
          {symbolsArray.map((symbol, index) => (
            <span key={index}>{symbol}</span>
          ))}
        </span>
      </button>
      {currentChat?.id === "new" ? (
        <StartChat />
      ) : (
        <MainContent chat={currentChat} />
      )}
    </>
  );
}
