import SlideHeader from "./SlideHeader";
import SlideDraft from "./SlideDraft";
import SlideEdit from "./SlideEdit";

export default function SlideArea({
  slides,
  selectedSlideId,
  onSelectedSlide,
  currentVersion,
  currentSlideState,
  setSlides,
  onInPresentationChange,
}) {
  const currentIndex = slides.findIndex((s) => s.slideID === selectedSlideId);
  const currentActualIndex = currentIndex !== -1 ? currentIndex : 0;

  // Обработчик для клика "Влево"
  const handleMoveLeft = () => {
    if (slides.length <= 1) return;
    const prevIndex = currentActualIndex === 0 ? 0 : currentActualIndex - 1;
    onSelectedSlide(slides[prevIndex].slideID);
  };

  // Обработчик для клика "Вправо"
  const handleMoveRight = () => {
    if (slides.length <= 1) return;
    const nextIndex =
      currentActualIndex === slides.length - 1
        ? slides.length - 1
        : currentActualIndex + 1;
    onSelectedSlide(slides[nextIndex].slideID);
  };

  return (
    <div id="slide-switcher" className="slide-switcher">
      <input
        type="image"
        src="./images/triangle.svg"
        id="move-to-left"
        className="move left"
        name="move-to-left"
        onClick={handleMoveLeft}
      />
      <div id="slide" className="slide">
        <SlideHeader
          slides={slides}
          currentActualIndex={currentActualIndex}
          selectedSlideId={selectedSlideId}
          onSelectedSlide={onSelectedSlide}
          currentSlideState={currentSlideState}
          onInPresentationChange={onInPresentationChange}
          currentVersionId={currentVersion.versionID}
        />
        <SlideDraft draft={currentVersion} />
        <SlideEdit />
      </div>
      <input
        type="image"
        src="./images/triangle.svg"
        id="move-to-right"
        className="move"
        name="move-to-right"
        onClick={handleMoveRight}
      />
    </div>
  );
}
