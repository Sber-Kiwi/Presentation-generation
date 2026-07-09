export default function SlideDraft({ draft, disabled }) {
  const title = draft?.slide?.meta?.title;
  const objects = draft?.slide?.objects ?? [];

  return (
    <div
      id="draft"
      className={`draft ${disabled ? "draft-disabled" : ""}`}
      aria-busy={disabled || undefined}
    >
      <div id="slide-title" className="slide-title">
        {title}
      </div>
      <div id="objects-grid" className="objects-grid">
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

        {objects.map((object, index) => (
          <div
            key={`obj-${index}`}
            className="grid-item"
            style={{
              gridColumn: `${object.cell_pos.x} / span ${object.span.x}`,
              gridRow: `${object.cell_pos.y} / span ${object.span.y}`,
              border: "2px solid #333",
              borderRadius: "4px",
              backgroundColor: "#fff",
            }}
          >
            <p>{object.type}</p>
            <p>{object.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
