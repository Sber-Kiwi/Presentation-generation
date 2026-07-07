export default function SlideHeader({
  slides,
  currentActualIndex,
  selectedSlideId,
  onSelectedSlide,
  currentSlideState,
  onInPresentationChange,
  currentVersionId,
}) {
  const handleSelectChange = (e) => {
    onSelectedSlide(e.target.value);
  };

  return (
    <div id="header" className="header">
      <div className="slide-number">
        Слайд {currentActualIndex + 1}/{slides.length}
      </div>
      <select
        className="slide-select"
        id="slide-select"
        value={selectedSlideId}
        onChange={handleSelectChange}
      >
        {slides.map((slide, index) => {
          const slideTitle = slide.versions.find(
            (version) => version.versionID === slide.state.selectedVersionID,
          )?.slide?.meta?.title;

          return (
            <option key={slide.slideID} value={slide.slideID}>
              Слайд {index + 1}. {slideTitle}
            </option>
          );
        })}
      </select>
      <div>
        <label htmlFor="include-slide-checkbox">Входит</label>
        <input
          type="checkbox"
          id="include-slide-checkbox"
          className="include-slide-checkbox"
          name="include-slide-checkbox"
          checked={currentSlideState?.inPresentation || false}
          onChange={(e) => onInPresentationChange?.(e.target.checked)}
        />
      </div>
    </div>
  );
}
