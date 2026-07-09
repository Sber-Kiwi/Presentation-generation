import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import SlideArea from "./SlideArea";
import VersionsPanel from "./VersionsPanel";
import { api, pollUntilTerminal, POLL_INTERVAL_MS } from "../api";

const MainContent = forwardRef(function MainContent(
  { chatId, chatTitle, slides, setSlides, onSave, globalBusy, notify },
  ref,
) {
  const [selectedSlideId, setSelectedSlideId] = useState(slides[0]?.slideID);

  const [editDrafts, setEditDrafts] = useState({});
  const [editingSlideIds, setEditingSlideIds] = useState(() => new Set());
  const [editErrors, setEditErrors] = useState({});

  const slidesRef = useRef(slides);
  useEffect(() => {
    slidesRef.current = slides;
  }, [slides]);

  const dirtySlideIdsRef = useRef(new Set());

  const currentSlide = slides.find(
    (slide) => slide.slideID === selectedSlideId,
  );
  const selectedVersionId = currentSlide?.state?.selectedVersionID;
  const currentVersion = currentSlide?.versions.find(
    (version) => version.versionID === selectedVersionId,
  );

  const isCurrentSlideEditing = editingSlideIds.has(selectedSlideId);

  const isAnySlideEditing = editingSlideIds.size > 0;

  const hasUnappliedEdit = Object.values(editDrafts).some(
    (text) => (text || "").trim().length > 0,
  );

  function toSlideVersionPayload(version) {
    return {
      versionID: version.versionID,
      slide: {
        meta: {
          title: version.slide?.meta?.title ?? null,
          notes: version.slide?.meta?.notes ?? null,
        },
        objects: version.slide?.objects ?? [],
      },
      createdAt: version.createdAt,
    };
  }

  // Отправляет накопленные drag-and-drop изменения одного слайда на бэкенд
  // как новую версию: POST .../versions.
  async function flushSlideVersion(slideId) {
    if (!dirtySlideIdsRef.current.has(slideId)) return;

    const slide = slidesRef.current.find((s) => s.slideID === slideId);
    const versionId = slide?.state?.selectedVersionID;
    const version = slide?.versions.find((v) => v.versionID === versionId);
    if (!slide || !version) {
      dirtySlideIdsRef.current.delete(slideId);
      return;
    }

    try {
      await api.createSlideVersion(
        chatId,
        slideId,
        toSlideVersionPayload(version),
      );
      dirtySlideIdsRef.current.delete(slideId);
    } catch (err) {
      notify?.(
        err.message ||
          "Не удалось отправить расположение объектов на слайде. Изменения будут отправлены позже.",
        "error",
      );
      throw err;
    }
  }

  // Отправляет несохранённые изменения по всем слайдам сразу. Используется
  // перед сохранением презентации и перед переходом в другой чат.
  async function flushAllPendingVersions() {
    const idsToFlush = Array.from(dirtySlideIdsRef.current);
    for (const slideId of idsToFlush) {
      try {
        await flushSlideVersion(slideId);
      } catch (_err) {
        // Ошибка уже показана пользователю внутри flushSlideVersion —
        // продолжаем со следующим слайдом, не прерывая общий флаш.
      }
    }
  }

  useImperativeHandle(ref, () => ({
    flushPendingChanges: flushAllPendingVersions,
  }));

  const handleSaveClick = () => {
    if (hasUnappliedEdit) {
      const confirmed = window.confirm(
        "У вас осталась непримененная правка. Вы уверены, что хотите продолжить?",
      );
      if (!confirmed) return;
    }
    onSave();
  };

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

  // Drag-and-drop в SlideDraft меняет расположение объектов только внутри
  // выбранной сейчас версии выбранного сейчас слайда — пишем изменения
  // туда же, откуда currentVersion.slide.objects был прочитан, и помечаем
  // слайд "грязным": на бэкенд эти изменения уйдут отдельной версией только
  // при сохранении презентации, отправке правки или смене чата.
  const handleObjectsChange = (newObjects) => {
    const slideId = selectedSlideId;
    dirtySlideIdsRef.current.add(slideId);
    setSlides((prevSlides) =>
      prevSlides.map((slide) => {
        if (slide.slideID !== slideId) return slide;
        return {
          ...slide,
          versions: slide.versions.map((version) =>
            version.versionID === selectedVersionId
              ? {
                  ...version,
                  slide: { ...version.slide, objects: newObjects },
                }
              : version,
          ),
        };
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

    setEditErrors((prev) => ({ ...prev, [slideId]: null }));
    setEditingSlideIds((prev) => new Set(prev).add(slideId));

    try {
      // Если пользователь до этого подвигал объекты на слайде и не сохранил
      // презентацию — сначала отправляем эти изменения отдельной версией
      // (fire-and-forget, без ожидания ответа), чтобы бэкенд знал о них
      // раньше правки. selectedVersionID при этом не меняется.
      await flushSlideVersion(slideId);

      const slide = slidesRef.current.find((s) => s.slideID === slideId);
      const versionID = slide?.state?.selectedVersionID;
      const baseVersion = slide?.versions.find(
        (v) => v.versionID === versionID,
      );

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

      const isChanged =
        JSON.stringify(newVersion.slide) !== JSON.stringify(baseVersion?.slide);

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
      notify?.(
        isChanged
          ? "Правки были применены. Слайд изменен."
          : "Слайд не был изменен.",
        isChanged ? "success" : "info",
      );
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
          onObjectsChange={handleObjectsChange}
        />
        <VersionsPanel
          versions={currentSlide.versions}
          selectedVersionId={selectedVersionId}
          onSelectVersion={handleVersionChange}
          onSave={handleSaveClick}
          versionsDisabled={isCurrentSlideEditing || globalBusy}
          saveDisabled={isAnySlideEditing || globalBusy}
        />
      </div>
    </div>
  );
});

export default MainContent;
