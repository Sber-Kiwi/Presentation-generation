import { useEffect, useState } from "react";

// Полноэкранный оверлей загрузки: перекрывает всё приложение и не даёт
// ничего нажать, пока идёт генерация / правка / экспорт.
// TODO: когда появится дизайн, заменить .spinner на gif в центре —
// разметка и смена подписей уже готовы для этого (messages).
export default function BlockingLoader({ messages = ["Загрузка..."] }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
    if (messages.length <= 1) return undefined;
    const timer = setInterval(() => {
      setIndex((i) => (i + 1) % messages.length);
    }, 2200);
    return () => clearInterval(timer);
  }, [messages]);

  return (
    <div className="blocking-loader">
      <div className="blocking-loader-box">
        <div className="spinner" />
        <p className="blocking-loader-text">{messages[index]}</p>
      </div>
    </div>
  );
}
