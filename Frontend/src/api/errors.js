// Единый класс ошибки для всех вызовов API (и мок, и настоящий бэкенд
// бросают именно его), чтобы компоненты могли одинаково читать err.message.
export class ApiError extends Error {
  constructor(message, { status, code, details } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status ?? null;
    this.code = code ?? null;
    this.details = details ?? null;
  }
}
