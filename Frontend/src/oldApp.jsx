import { useState } from "react";

export default function App() {
  const [isOpen, setIsOpen] = useState(true);

  const toggleChats = () => {
    setIsOpen(!isOpen);
  };

  const arrowSymbol = isOpen ? "<" : ">";
  const symbolsArray = Array(50).fill(arrowSymbol);

  return (
    <>
      <div id="chats" className={`chats ${isOpen ? "" : "collapsed"}`}>
        <input
          type="button"
          id="new-chat"
          className="new-chat"
          defaultValue="+"
        />
        <input type="button" className="chat" defaultValue="Чат 1" />
        <input type="button" className="chat" defaultValue="Чат 2" />
        <input type="button" className="chat" defaultValue="Чат 3" />
      </div>
      <button id="toggle-chats" className="toggle-chats" onClick={toggleChats}>
        <span className="symbol-chain">
          {symbolsArray.map((symbol, index) => (
            <span key={index}>{symbol}</span>
          ))}
        </span>
      </button>
      <div id="main" className="main">
        <p className="presentation-title">Название презентации</p>
        <div id="presentation-editor" className="presentation-editor">
          <div id="slide-switcher" className="slide-switcher">
            <input
              type="image"
              src="./images/triangle.svg"
              id="move-to-left"
              className="move left"
              name="move-to-left"
            />
            <div id="slide" className="slide">
              <div id="header" className="header">
                <div className="slide-number">Слайд 1/N</div>
                <select className="slide-select" id="slide-select">
                  <option defaultValue="0">
                    Слайд 1. В котором рассказывается его путь становления и тд
                    и тп
                  </option>
                  <option defaultValue="1">Слайд 2.</option>
                  <option defaultValue="2">Слайд 3.</option>
                </select>
                <div>
                  <label htmlFor="include-slide-checkbox">Входит</label>
                  <input
                    type="checkbox"
                    defaultChecked=""
                    id="include-slide-checkbox"
                    className="include-slide-checkbox"
                    name="include-slide-checkbox"
                  />
                </div>
              </div>
              <div id="draft" className="draft">
                <div id="slide-title" className="slide-title">
                  Название слайда
                </div>
                <div id="objects-grid" className="objects-grid">
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                  <div className="grid-item"></div>
                </div>
              </div>
              <div id="edits" className="edits">
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
            </div>
            <input
              type="image"
              src="./images/triangle.svg"
              id="move-to-right"
              className="move"
              name="move-to-right"
            />
          </div>
          <div id="versions-and-save" className="versions-and-save">
            <div id="versions" className="versions">
              <input
                type="button"
                className="version"
                defaultValue="Версия 1"
              />
              <input
                type="button"
                className="version"
                defaultValue="Версия 2"
              />
              <input
                type="button"
                className="version"
                defaultValue="Версия 3"
              />
            </div>
            <input
              type="button"
              id="save"
              className="save"
              name="save"
              defaultValue={`Сохранить\n презентацию`}
            />
          </div>
        </div>
      </div>
    </>
  );
}
