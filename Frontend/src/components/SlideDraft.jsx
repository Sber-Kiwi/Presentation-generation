import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

const GRID_COLS = 4;
const GRID_ROWS = 3;
const LOCKED_TYPE = "WATERFALL";

// Какие типы графиков можно менять между собой по клику на бейдж, и на
// что именно.
const TYPE_CONVERSIONS = {
  BAR_CHART: ["BAR_CHART", "LINE_CHART"],
  LINE_CHART: ["BAR_CHART", "LINE_CHART"],
  PIE_CHART: ["PIE_CHART", "BAR_CHART", "LINE_CHART"],
};

// Все 8 "ручек" для ресайза: направление кодируется буквами сторон,
// которые она тянет (n/s/e/w), как в PowerPoint/Google Slides.
const RESIZE_HANDLES = ["nw", "n", "ne", "e", "se", "s", "sw", "w"];

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

// Прямоугольник объекта в координатах сетки (1-indexed, включительно).
const toRect = (obj) => ({
  x: obj.cell_pos.x,
  y: obj.cell_pos.y,
  spanX: obj.span.x,
  spanY: obj.span.y,
});

const rectsOverlap = (a, b) =>
  a.x < b.x + b.spanX &&
  a.x + a.spanX > b.x &&
  a.y < b.y + b.spanY &&
  a.y + a.spanY > b.y;

const TYPE_COLORS = {
  TEXT: "#2563eb",
  TABLE: "#16a34a",
  PIE_CHART: "#9333ea",
  BAR_CHART: "#ea580c",
  LINE_CHART: "#0d9488",
  WATERFALL: "#64748b",
};

function getTypeColor(type) {
  if (TYPE_COLORS[type]) return TYPE_COLORS[type];
  let hash = 0;
  for (let i = 0; i < type.length; i += 1) {
    hash = type.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, 65%, 40%)`;
}

// Замеряем реальные размеры ячейки и отступов прямо из DOM, чтобы не
// зависеть от захардкоженных пикселей и не разъезжаться с CSS.
function getGridMetrics(gridEl) {
  const rect = gridEl.getBoundingClientRect();
  const style = getComputedStyle(gridEl);
  const colGap = parseFloat(style.columnGap) || 0;
  const rowGap = parseFloat(style.rowGap) || 0;
  const cellW = (rect.width - colGap * (GRID_COLS - 1)) / GRID_COLS;
  const cellH = (rect.height - rowGap * (GRID_ROWS - 1)) / GRID_ROWS;
  return {
    stepX: cellW + colGap,
    stepY: cellH + rowGap,
  };
}

function resizeAxis(low, high, startPos, startSpan, deltaCells, gridSize) {
  if (high) {
    const span = clamp(startSpan + deltaCells, 1, gridSize - startPos + 1);
    return { pos: startPos, span };
  }
  if (low) {
    const maxPos = startPos + startSpan - 1;
    const pos = clamp(startPos + deltaCells, 1, maxPos);
    const span = startPos + startSpan - pos;
    return { pos, span };
  }
  return { pos: startPos, span: startSpan };
}

function resolveResizeCollisions(rect, handle, otherRects) {
  const west = handle.includes("w");
  const north = handle.includes("n");
  const horizontal = handle.includes("e") || handle.includes("w");
  const vertical = handle.includes("n") || handle.includes("s");
  const r = { ...rect };
  let guard = 0;

  while (otherRects.some((o) => rectsOverlap(r, o)) && guard < 20) {
    guard += 1;
    let shrank = false;

    if (horizontal && r.spanX > 1) {
      if (west) {
        r.x += 1;
        r.spanX -= 1;
      } else {
        r.spanX -= 1;
      }
      shrank = true;
    } else if (vertical && r.spanY > 1) {
      if (north) {
        r.y += 1;
        r.spanY -= 1;
      } else {
        r.spanY -= 1;
      }
      shrank = true;
    }

    if (!shrank) break;
  }

  return r;
}

export default function SlideDraft({ draft, disabled, onObjectsChange }) {
  const title = draft?.slide?.meta?.title;
  const objects = draft?.slide?.objects ?? [];

  const gridRef = useRef(null);
  const [interaction, setInteraction] = useState(null);

  const [typeMenu, setTypeMenu] = useState(null);
  const typeMenuRef = useRef(null);

  useEffect(() => {
    if (!typeMenu) return undefined;
    const handleDocClick = (e) => {
      if (typeMenuRef.current?.contains(e.target)) return;
      setTypeMenu(null);
    };
    document.addEventListener("click", handleDocClick);
    return () => document.removeEventListener("click", handleDocClick);
  }, [typeMenu]);

  const commitObjects = (updater) => {
    if (!onObjectsChange) return;
    onObjectsChange(updater(objects));
  };

  const handleTypeSelect = (index, newType) => {
    commitObjects((prev) =>
      prev.map((o, i) => (i === index ? { ...o, type: newType } : o)),
    );
    setTypeMenu(null);
  };

  const handleBadgeClick = (e, index, options) => {
    if (disabled || !options) return;
    e.stopPropagation();
    const rect = e.currentTarget.getBoundingClientRect();
    setTypeMenu((prev) =>
      prev?.index === index
        ? null
        : {
            index,
            x: rect.left,
            y: rect.bottom,
            width: rect.width,
          },
    );
  };

  const beginMove = (e, index) => {
    if (disabled) return;
    const obj = objects[index];
    if (!obj || obj.type === LOCKED_TYPE) return;
    const grid = gridRef.current;
    if (!grid || e.button !== 0) return;

    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.setPointerCapture(e.pointerId);

    setInteraction({
      mode: "move",
      index,
      pointerId: e.pointerId,
      startX: e.clientX,
      startY: e.clientY,
      metrics: getGridMetrics(grid),
      startCellPos: { ...obj.cell_pos },
      startSpan: { ...obj.span },
      preview: {
        cellPos: { ...obj.cell_pos },
        span: { ...obj.span },
        status: "valid",
        swapIndex: null,
      },
    });
  };

  const beginResize = (e, index, handle) => {
    if (disabled) return;
    const obj = objects[index];
    if (!obj || obj.type === LOCKED_TYPE) return;
    const grid = gridRef.current;
    if (!grid || e.button !== 0) return;

    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.setPointerCapture(e.pointerId);

    setInteraction({
      mode: "resize",
      handle,
      index,
      pointerId: e.pointerId,
      startX: e.clientX,
      startY: e.clientY,
      metrics: getGridMetrics(grid),
      startCellPos: { ...obj.cell_pos },
      startSpan: { ...obj.span },
      preview: {
        cellPos: { ...obj.cell_pos },
        span: { ...obj.span },
        status: "valid",
        swapIndex: null,
      },
    });
  };

  useEffect(() => {
    if (!interaction) return undefined;

    const handlePointerMove = (e) => {
      if (e.pointerId !== interaction.pointerId) return;

      const dx = e.clientX - interaction.startX;
      const dy = e.clientY - interaction.startY;
      const deltaCellX = Math.round(dx / interaction.metrics.stepX);
      const deltaCellY = Math.round(dy / interaction.metrics.stepY);

      const others = objects
        .map((o, i) => ({ obj: o, index: i }))
        .filter(({ index }) => index !== interaction.index);
      const otherRects = others.map(({ obj }) => toRect(obj));

      if (interaction.mode === "move") {
        const newX = clamp(
          interaction.startCellPos.x + deltaCellX,
          1,
          GRID_COLS,
        );
        const newY = clamp(
          interaction.startCellPos.y + deltaCellY,
          1,
          GRID_ROWS,
        );
        // Обрезаем объект, если он вылезает за границы сетки.
        const spanX = Math.min(interaction.startSpan.x, GRID_COLS - newX + 1);
        const spanY = Math.min(interaction.startSpan.y, GRID_ROWS - newY + 1);

        const targetRect = { x: newX, y: newY, spanX, spanY };
        const overlapping = others.filter(({ obj }) =>
          rectsOverlap(targetRect, toRect(obj)),
        );

        let status = "valid";
        let swapIndex = null;
        let previewCellPos = { x: newX, y: newY };
        let previewSpan = { x: spanX, y: spanY };

        if (overlapping.length > 0) {
          // Своп триггерится не совпадением размеров, а тем, что ЦЕНТР
          // перетаскиваемого объекта попал внутрь ровно одного другого
          // объекта — так можно менять местами объекты разных размеров,
          // не целясь пиксель в пиксель.
          const centerX = newX + spanX / 2;
          const centerY = newY + spanY / 2;
          const centerHit = overlapping.find(({ obj }) => {
            const r = toRect(obj);
            return (
              centerX > r.x &&
              centerX < r.x + r.spanX &&
              centerY > r.y &&
              centerY < r.y + r.spanY
            );
          });

          if (
            overlapping.length === 1 &&
            centerHit &&
            centerHit.obj.type !== LOCKED_TYPE
          ) {
            status = "swap";
            swapIndex = centerHit.index;
            previewCellPos = { ...centerHit.obj.cell_pos };
            previewSpan = { ...centerHit.obj.span };
          } else {
            status = "invalid";
          }
        }

        setInteraction((prev) =>
          prev
            ? {
                ...prev,
                preview: {
                  cellPos: previewCellPos,
                  span: previewSpan,
                  status,
                  swapIndex,
                },
              }
            : prev,
        );
        return;
      }

      const { handle } = interaction;
      const west = handle.includes("w");
      const east = handle.includes("e");
      const north = handle.includes("n");
      const south = handle.includes("s");

      const { pos: x, span: spanX } =
        west || east
          ? resizeAxis(
              west,
              east,
              interaction.startCellPos.x,
              interaction.startSpan.x,
              deltaCellX,
              GRID_COLS,
            )
          : { pos: interaction.startCellPos.x, span: interaction.startSpan.x };

      const { pos: y, span: spanY } =
        north || south
          ? resizeAxis(
              north,
              south,
              interaction.startCellPos.y,
              interaction.startSpan.y,
              deltaCellY,
              GRID_ROWS,
            )
          : { pos: interaction.startCellPos.y, span: interaction.startSpan.y };

      const resolved = resolveResizeCollisions(
        { x, y, spanX, spanY },
        handle,
        otherRects,
      );

      setInteraction((prev) =>
        prev
          ? {
              ...prev,
              preview: {
                cellPos: { x: resolved.x, y: resolved.y },
                span: { x: resolved.spanX, y: resolved.spanY },
                status: "valid",
                swapIndex: null,
              },
            }
          : prev,
      );
    };

    const finish = (e) => {
      if (e.pointerId !== interaction.pointerId) return;

      const { mode, index, preview, startCellPos, startSpan } = interaction;

      if (mode === "resize" || preview.status === "valid") {
        commitObjects((prev) =>
          prev.map((o, i) =>
            i === index
              ? { ...o, cell_pos: preview.cellPos, span: preview.span }
              : o,
          ),
        );
      } else if (mode === "move" && preview.status === "swap") {
        const { swapIndex } = preview;
        commitObjects((prev) => {
          const target = prev[swapIndex];
          if (!target) return prev;
          return prev.map((o, i) => {
            if (i === index) {
              return { ...o, cell_pos: target.cell_pos, span: target.span };
            }
            if (i === swapIndex) {
              return { ...o, cell_pos: startCellPos, span: startSpan };
            }
            return o;
          });
        });
      }

      setInteraction(null);
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", finish);
    window.addEventListener("pointercancel", finish);
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", finish);
      window.removeEventListener("pointercancel", finish);
    };
  }, [interaction, objects]);

  return (
    <div
      id="draft"
      className={`draft ${disabled ? "draft-disabled" : ""}`}
      aria-busy={disabled || undefined}
    >
      <div id="slide-title" className="slide-title">
        <span className="slide-title-text">{title}</span>
      </div>
      <div id="objects-grid" className="objects-grid" ref={gridRef}>
        {Array.from({ length: 12 }, (_, i) => ({
          col: (i % 4) + 1,
          row: Math.floor(i / 4) + 1,
        })).map((pos, index) => (
          <div
            key={`bg-${index}`}
            className="grid-item-bg"
            style={{
              gridColumn: pos.col,
              gridRow: pos.row,
            }}
          />
        ))}

        {objects.map((object, index) => {
          const isLocked = object.type === LOCKED_TYPE;
          const isDragged = interaction?.index === index;
          const isSwapGhost =
            interaction?.mode === "move" &&
            interaction.preview.status === "swap" &&
            interaction.preview.swapIndex === index;

          let cellPos = object.cell_pos;
          let span = object.span;
          let status = null;

          if (isDragged) {
            cellPos = interaction.preview.cellPos;
            span = interaction.preview.span;
            status = interaction.preview.status;
          } else if (isSwapGhost) {
            cellPos = interaction.startCellPos;
            span = interaction.startSpan;
            status = "swap";
          }

          const statusClass =
            status === "invalid"
              ? "grid-item-invalid"
              : status === "swap"
                ? "grid-item-swap"
                : "";

          return (
            <div
              key={`obj-${index}`}
              className={`grid-item ${isLocked ? "grid-item-locked" : ""} ${
                isDragged || isSwapGhost ? "grid-item-interacting" : ""
              } ${statusClass}`}
              style={{
                gridColumn: `${cellPos.x} / span ${span.x}`,
                gridRow: `${cellPos.y} / span ${span.y}`,
              }}
              onPointerDown={(e) => beginMove(e, index)}
            >
              <div className="grid-item-content">
                {(() => {
                  const options = TYPE_CONVERSIONS[object.type];
                  const isClickable = !isLocked && !!options && !disabled;
                  if (!isClickable) {
                    return (
                      <span
                        className="type-badge"
                        style={{ backgroundColor: getTypeColor(object.type) }}
                      >
                        {object.type}
                      </span>
                    );
                  }
                  return (
                    <button
                      type="button"
                      className="type-badge type-badge-clickable"
                      style={{ backgroundColor: getTypeColor(object.type) }}
                      onPointerDown={(e) => e.stopPropagation()}
                      onClick={(e) => handleBadgeClick(e, index, options)}
                    >
                      {object.type}
                    </button>
                  );
                })()}
                {object.title && (
                  <p className="grid-item-title">{object.title}</p>
                )}
                {object.data_description && (
                  <p className="grid-item-text">{object.data_description}</p>
                )}
              </div>

              {!isLocked &&
                RESIZE_HANDLES.map((handle) => (
                  <div
                    key={handle}
                    className={`resize-handle resize-handle-${handle}`}
                    onPointerDown={(e) => beginResize(e, index, handle)}
                  />
                ))}
            </div>
          );
        })}
      </div>

      {typeMenu &&
        (() => {
          const obj = objects[typeMenu.index];
          const options = obj ? TYPE_CONVERSIONS[obj.type] : null;
          if (!obj || !options) return null;
          return createPortal(
            <div
              ref={typeMenuRef}
              className="type-menu"
              style={{
                top: typeMenu.y + 4,
                left: typeMenu.x,
                minWidth: typeMenu.width,
              }}
            >
              {options.map((opt) => (
                <button
                  key={opt}
                  type="button"
                  className={`type-menu-option ${
                    opt === obj.type ? "type-menu-option-active" : ""
                  }`}
                  onClick={() => handleTypeSelect(typeMenu.index, opt)}
                >
                  <span
                    className="type-menu-dot"
                    style={{ backgroundColor: getTypeColor(opt) }}
                  />
                  {opt}
                </button>
              ))}
            </div>,
            document.body,
          );
        })()}
    </div>
  );
}
