import { useState } from "react";
import SlideArea from "./SlideArea";
import VersionsPanel from "./VersionsPanel";

export default function MainContent({ chatTitle, slides, setSlides, onSave }) {
  const [selectedSlideId, setSelectedSlideId] = useState(slides[0]?.slideID);
  const currentSlide = slides.find(
    (slide) => slide.slideID === selectedSlideId,
  );

  const selectedVersionId = currentSlide?.state?.selectedVersionID;
  const currentVersion = currentSlide?.versions.find(
    (version) => version.versionID === selectedVersionId,
  );

  // 5. Умный обработчик изменения версии (клик в VersionsPanel)
  const handleVersionChange = (newVersionId) => {
    // Иммутабельно обновляем JSON в стейте App.jsx
    setSlides((prevSlides) =>
      prevSlides.map((slide) => {
        if (slide.slideID === selectedSlideId) {
          return {
            ...slide,
            state: {
              ...slide.state,
              selectedVersionID: newVersionId, // Перезаписываем выбранную версию в памяти
            },
          };
        }
        return slide;
      }),
    );
  };

  const handleInPresentationChange = (isChecked) => {
    setSlides((prevSlides) =>
      prevSlides.map((slide) => {
        if (slide.slideID === selectedSlideId) {
          return {
            ...slide,
            state: {
              ...slide.state,
              inPresentation: isChecked, // Перезаписываем выбранную версию в памяти
            },
          };
        }
        return slide;
      }),
    );
  };

  return (
    <div id="main" className="main">
      <p className="presentation-title">{chatTitle}</p>
      <div id="presentation-editor" className="presentation-editor">
        <SlideArea
          slides={slides}
          selectedSlideId={selectedSlideId}
          onSelectedSlide={setSelectedSlideId}
          currentVersion={currentVersion}
          currentSlideState={currentSlide?.state}
          setSlides={setSlides}
          onInPresentationChange={handleInPresentationChange}
        />
        <VersionsPanel
          versions={currentSlide.versions}
          selectedVersionId={selectedVersionId}
          onSelectVersion={handleVersionChange}
          onSave={onSave}
        />
      </div>
    </div>
  );
}
