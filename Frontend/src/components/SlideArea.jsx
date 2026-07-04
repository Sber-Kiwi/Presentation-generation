import SlideHeader from "./SlideHeader";
import SlideDraft from "./SlideDraft";
import SlideEdit from "./SlideEdit";

export default function SlideArea({
  slides,
  selectedSlideId,
  onSelectedSlide,
  currentVersion,
}) {
  return (
    <div id="slide-switcher" className="slide-switcher">
      <input
        type="image"
        src="./images/triangle.svg"
        id="move-to-left"
        className="move left"
        name="move-to-left"
      />
      <div id="slide" className="slide">
        <SlideHeader />
        <SlideDraft />
        <SlideEdit />
      </div>
      <input
        type="image"
        src="./images/triangle.svg"
        id="move-to-right"
        className="move"
        name="move-to-right"
      />
    </div>
  );
}
