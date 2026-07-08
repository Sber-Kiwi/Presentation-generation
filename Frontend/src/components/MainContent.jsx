import { useState } from "react";
import SlideArea from "./SlideArea";
import VersionsPanel from "./VersionsPanel";
import { api, pollUntilTerminal, POLL_INTERVAL_MS } from "../api";

export default function MainContent({
  chatId,
  chatTitle,
  slides,
  setSlides,
  onSave,
  globalBusy,
}) {
  const [selectedSlideId, setSelectedSlideId] = useState(slides[0]?.slideID);

  // У каждого слайда — своё поле для правок и свой статус выполнения.
  const [editDrafts, setEditDrafts] = useState({});
  const [editingSlideIds, setEditingSlideIds] = useState(() => new Set());
  const [editErrors, setEditErrors] = useState({});

  const currentSlide = slides.find(
    (slide) => slide.slideID === selectedSlideId,
  );
  const selectedVersionId = currentSlide?.state?.selectedVersionID;
  const currentVersion = currentSlide?.versions.find(
    (version) => version.versionID === selectedVersionId,
  );

  const isCurrentSlideEditing = editingSlideIds.has(selectedSlideId);
  // Пока правится хотя бы один слайд, кнопка "Сохранить презентацию"
  // заблокирована для всего чата.
  const isAnySlideEditing = editingSlideIds.size > 0;

  const handleVersionChange = (newVersionId) => {
    if (isCurrentSlideEditing || globalBusy) return;
    setSlides((prevSlides) =>
      prevSlides.map((slide) => {
        if (slide.slideID === selectedSlideId) {
          return {
            ...slide,
            state: { ...slide.state, selectedVersionID: newVersionId },
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
            state: { ...slide.state, inPresentation: isChecked },
          };
        }
        return slide;
      }),
    );
  };

  const handleEditDraftChange = (slideId, text) => {
    setEditDrafts((prev) => ({ ...prev, [slideId]: text }));
  };

  const handleSubmitEdit = async (slideId) => {
    const prompt = (editDrafts[slideId] || "").trim();
    // Кнопка отправки правки недоступна, если поле пустое.
    if (!prompt || editingSlideIds.has(slideId) || globalBusy) return;

    const slide = slides.find((s) => s.slideID === slideId);
    const versionID = slide?.state?.selectedVersionID;

    setEditErrors((prev) => ({ ...prev, [slideId]: null }));
    setEditingSlideIds((prev) => new Set(prev).add(slideId));

    try {
      const { taskID } = await api.createSlideEdit(chatId, slideId, {
        prompt,
        versionID,
      });

      const finalStatus = await pollUntilTerminal(
        () => api.getSlideEditStatus(chatId, slideId, taskID),
        { intervalMs: POLL_INTERVAL_MS },
      );

      if (finalStatus.status === "failed") {
        throw new Error(finalStatus.error || "Не удалось применить правку");
      }

      const newVersion = await api.getSlide(
        chatId,
        slideId,
        finalStatus.newVersionID,
      );

      setSlides((prevSlides) =>
        prevSlides.map((s) => {
          if (s.slideID !== slideId) return s;
          return {
            ...s,
            versions: [
              ...s.versions,
              {
                versionID: newVersion.versionID,
                slide: newVersion.slide,
                createdAt: newVersion.createdAt,
              },
            ],
            state: { ...s.state, selectedVersionID: newVersion.versionID },
          };
        }),
      );
      setEditDrafts((prev) => ({ ...prev, [slideId]: "" }));
    } catch (err) {
      setEditErrors((prev) => ({
        ...prev,
        [slideId]: err.message || "Ошибка при правке слайда",
      }));
    } finally {
      setEditingSlideIds((prev) => {
        const next = new Set(prev);
        next.delete(slideId);
        return next;
      });
    }
  };

  if (!currentSlide) return null;

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
          onInPresentationChange={handleInPresentationChange}
          editValue={editDrafts[selectedSlideId] || ""}
          onEditChange={(text) => handleEditDraftChange(selectedSlideId, text)}
          onSubmitEdit={() => handleSubmitEdit(selectedSlideId)}
          isEditing={isCurrentSlideEditing}
          editError={editErrors[selectedSlideId]}
        />
        <VersionsPanel
          versions={currentSlide.versions}
          selectedVersionId={selectedVersionId}
          onSelectVersion={handleVersionChange}
          onSave={onSave}
          disabled={isAnySlideEditing || globalBusy}
        />
      </div>
    </div>
  );
}
