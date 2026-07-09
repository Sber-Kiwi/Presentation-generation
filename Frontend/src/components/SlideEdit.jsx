export default function SlideEdit({
  value,
  onChange,
  onSubmit,
  disabled,
  error,
}) {
  // Нельзя нажать кнопку отправки, если поле пустое или правка уже выполняется.
  const canSend = !disabled && value.trim().length > 0;

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (canSend) onSubmit();
    }
  };

  return (
    <div className="slide-edit-wrapper">
      <div id="edit" className="edit">
        <textarea
          id="comment"
          className="comment"
          name="comment"
          placeholder={disabled ? "Правка выполняется..." : "Поле для правок"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />
        <input
          type="image"
          src="./images/send.svg"
          id="send-edit"
          className="send-edit"
          name="send-edit"
          alt="Отправить правку"
          onClick={() => canSend && onSubmit()}
          style={{
            opacity: canSend ? 1 : 0.4,
            cursor: canSend ? "pointer" : "not-allowed",
          }}
        />
      </div>
      <div className="edit-status">
        {disabled ? (
          <p className="hint-text">Слайд обновляется, подождите...</p>
        ) : error ? (
          <p className="error-text">{error}</p>
        ) : null}
      </div>
    </div>
  );
}
