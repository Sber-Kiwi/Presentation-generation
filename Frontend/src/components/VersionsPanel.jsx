export default function VersionPanel({
  versions,
  selectedVersionId,
  onSelectVersion,
  onSave,
  versionsDisabled,
  saveDisabled,
}) {
  return (
    <div id="versions-and-save" className="versions-and-save">
      <div id="versions" className="versions">
        {versions.map((version, index) => (
          <button
            key={version.versionID}
            className={`version ${version.versionID === selectedVersionId ? "active" : ""}`}
            onClick={() =>
              !versionsDisabled && onSelectVersion(version.versionID)
            }
            disabled={versionsDisabled}
          >
            Версия {index + 1}
          </button>
        ))}
      </div>

      <button
        id="save"
        className="save"
        name="save"
        onClick={onSave}
        disabled={saveDisabled}
      >
        Сохранить <br /> презентацию
      </button>
    </div>
  );
}
