export default function SlideEdit() {
  return (
    <div id="edit" className="edit">
      <textarea
        id="comment"
        className="comment"
        name="comment"
        placeholder="Поле для правок"
        defaultValue={""}
      />
      <input
        type="image"
        src="./images/send.svg"
        id="send-edit"
        className="send-edit"
        name="send-edit"
      />
    </div>
  );
}
