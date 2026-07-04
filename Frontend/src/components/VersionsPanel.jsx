export default function VersionPanel({
  versions,
  selectedVersionId,
  onSelectVersion,
}) {
  return (
    <div id="versions-and-save" className="versions-and-save">
      <div id="versions" className="versions">
        {versions.map((version, index) => (
          <button
            key={version.versionID}
            className={`version ${version.versionID === selectedVersionId ? "active" : ""}`}
            onClick={() => onSelectVersion(version.versionID)}
          >
            Версия {index + 1}
          </button>
        ))}
      </div>

      <button id="save" className="save" name="save">
        {`Сохранить\n презентацию`}
      </button>
    </div>
  );
}
