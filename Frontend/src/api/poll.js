export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Опрашивает статус задачи, пока она не перейдёт в терминальное состояние
 * (done / failed). Используется для генерации презентации, правки слайда
 * и экспорта — все три сценария устроены одинаково: POST запускает задачу,
 * а дальше нужно поллить GET .../status до done/failed.
 *
 * @param {() => Promise<{status: string, [key: string]: any}>} fetchStatus
 * @param {{intervalMs?: number, terminalStatuses?: string[], onTick?: (status: any) => void}} options
 */
export async function pollUntilTerminal(
  fetchStatus,
  { intervalMs = 1200, terminalStatuses = ["done", "failed"], onTick } = {},
) {
  let status = await fetchStatus();
  onTick?.(status);

  while (!terminalStatuses.includes(status.status)) {
    await sleep(intervalMs);
    status = await fetchStatus();
    onTick?.(status);
  }

  return status;
}
