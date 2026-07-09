import { useRef, useState } from "react";

export default function StartChat({ onSubmit, disabled, error }) {
  const [prompt, setPrompt] = useState("");
  const [file, setFile] = useState(null);
  const [localError, setLocalError] = useState(null);
  const fileInputRef = useRef(null);

  // Кнопку отправки нельзя нажать без текста запроса и без csv-файла.
  const canSend = !disabled && prompt.trim().length > 0 && !!file;

  const handleAttachClick = () => {
    if (disabled) return;
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0] ?? null;
    e.target.value = ""; // позволяет выбрать тот же файл ещё раз
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setLocalError("Нужен файл в формате .csv");
      return;
    }
    setLocalError(null);
    setFile(selected);
  };

  const handleRemoveFile = () => {
    if (disabled) return;
    setFile(null);
  };

  const handleSubmit = () => {
    if (disabled) return;
    const hasPrompt = prompt.trim().length > 0;
    const hasFile = !!file;

    if (!hasPrompt && !hasFile) {
      setLocalError("Добавьте текст запроса и CSV-файл.");
      return;
    }
    if (!hasPrompt) {
      setLocalError("Добавьте текст запроса.");
      return;
    }
    if (!hasFile) {
      setLocalError("Добавьте CSV-файл.");
      return;
    }

    setLocalError(null);
    onSubmit(prompt.trim(), file);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const shownError = localError || error;

  return (
    <div className="start">
      <h1 className="greeting">Good afternoon, Эрик!</h1>

      <div className="start-input">
        <div className="edit">
          <input
            type="image"
            src="images/paperclip.svg"
            className="send"
            name="paperclip"
            alt="Прикрепить файл"
            onClick={handleAttachClick}
            style={{
              opacity: disabled ? 0.4 : 1,
              cursor: disabled ? "not-allowed" : "pointer",
            }}
          />
          <input
            type="file"
            accept=".csv,text/csv"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          <textarea
            className="comment"
            name="comment"
            placeholder="Введите запрос и прикрепите таблицу с данными"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
          />
          <input
            type="image"
            src="images/send.svg"
            className="send"
            name="send-edit"
            alt="Отправить"
            onClick={handleSubmit}
            style={{
              opacity: canSend ? 1 : 0.4,
              cursor: canSend ? "pointer" : "not-allowed",
            }}
          />
        </div>

        {file && (
          <div className="attached-file">
            <span className="attached-file-name">📎 {file.name}</span>
            <button
              type="button"
              className="remove-file"
              onClick={handleRemoveFile}
              disabled={disabled}
              aria-label="Убрать файл"
            >
              ×
            </button>
          </div>
        )}

        {shownError && <p className="error-text">{shownError}</p>}
      </div>
    </div>
  );
}
