import { useEffect } from "react";

export default function Notification({ notice, onClose }) {
  useEffect(() => {
    if (!notice) return undefined;
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [notice, onClose]);

  if (!notice) return null;

  return (
    <div className={`notification notification-${notice.type}`} role="status">
      <span>{notice.text}</span>
      <button
        type="button"
        className="notification-close"
        onClick={onClose}
        aria-label="Закрыть"
      >
        ×
      </button>
    </div>
  );
}
