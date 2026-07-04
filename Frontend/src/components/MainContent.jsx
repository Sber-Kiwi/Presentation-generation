import { useState } from "react";
import SlideArea from "./SlideArea";
import VersionsPanel from "./VersionsPanel";

export default function MainContent({ chat }) {
  const [selectedSlideId, setSelectedSlideId] = useState(
    chat.slides[0]?.slideID,
  );
  const currentSlide = chat.slides.find(
    (slide) => slide.slideID === selectedSlideId,
  );

  const [selectedVersionId, setSelectedVersionId] = useState(
    currentSlide.versions[0]?.versionID,
  );
  const currentVersion = currentSlide.versions.find(
    (version) => version.versionID === selectedVersionId,
  );

  return (
    <div id="main" className="main">
      <p className="presentation-title">{chat.title}</p>
      <div id="presentation-editor" className="presentation-editor">
        <SlideArea
          slides={chat.slides}
          selectedSlideId={selectedSlideId}
          onSelectedSlide={setSelectedSlideId}
          currentVersion={currentVersion}
        />
        <VersionsPanel
          versions={currentSlide.versions}
          selectedVersionId={selectedVersionId}
          onSelectVersion={setSelectedVersionId}
        />
      </div>
    </div>
  );
}
