export default function Sidebar({
  isOpen,
  chats,
  selectedChatId,
  onSelectChat,
}) {
  return (
    <div id="chats" className={`chats ${isOpen ? "" : "collapsed"}`}>
      {chats.map((chat) => {
        if (chat?.id === "new") {
          return (
            <button
              key={chat.id}
              className={`new-chat ${chat.id === selectedChatId ? "active" : ""}`}
              onClick={() => onSelectChat(chat.id)}
            >
              +
            </button>
          );
        } else {
          return (
            <button
              key={chat.id}
              className={`chat ${chat.id === selectedChatId ? "active" : ""}`}
              onClick={() => onSelectChat(chat.id)}
            >
              {chat.title}
            </button>
          );
        }
      })}
    </div>
  );
}
