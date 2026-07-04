export default function SlideHeader() {
  return (
    <div id="header" className="header">
      <div className="slide-number">Слайд 1/N</div>
      <select className="slide-select" id="slide-select">
        <option defaultValue="0">
          Слайд 1. В котором рассказывается его путь становления и тд и тп
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
  );
}
