export default function StartChat() {
  return (
    <div className="start">
      <h1 className="greeting">Good afternoon, Эрик!</h1>
      <div className="edit">
        <input
          type="image"
          src="images/paperclip.svg"
          className="send"
          name="paperclip"
        />
        <textarea
          className="comment"
          name="comment"
          placeholder="Введите запрос и прикрепите таблицу с данными"
          defaultValue={""}
        />
        <input
          type="image"
          src="images/send.svg"
          className="send"
          name="send-edit"
        />
      </div>
    </div>
  );
}
