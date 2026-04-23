import { logger, schedules } from "@trigger.dev/sdk/v3";

// Tune-me constant — change here, not inline in the cron string.
// Directive asked for 15m, operator note requested every 6h for now.
const CRON_EVERY_6_HOURS = "0 */6 * * *";

const DISPATCH_PATH = "/api/internal/scheduler/dispatch-due-preframes";

export const serxSchedulerTick = schedules.task({
  id: "serx:scheduler-tick",
  cron: CRON_EVERY_6_HOURS,
  maxDuration: 60,
  run: async (payload) => {
    const apiUrl = process.env.SERX_API_URL;
    const token = process.env.SERX_INTERNAL_TOKEN;

    if (!apiUrl || !token) {
      throw new Error(
        "SERX_API_URL and SERX_INTERNAL_TOKEN must be set in Trigger.dev env vars",
      );
    }

    const url = `${apiUrl.replace(/\/$/, "")}${DISPATCH_PATH}`;
    logger.info("dispatching due preframes", {
      scheduledFor: payload.timestamp.toISOString(),
      url,
    });

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });

    const bodyText = await response.text();
    if (!response.ok) {
      logger.error("scheduler dispatch failed", {
        status: response.status,
        body: bodyText.slice(0, 2000),
      });
      throw new Error(
        `SERX scheduler dispatch failed: HTTP ${response.status}`,
      );
    }

    let summary: unknown = bodyText;
    try {
      summary = JSON.parse(bodyText);
    } catch {
      // non-JSON response is unexpected but not fatal for the tick itself
    }

    logger.info("scheduler dispatch ok", { summary });
    return summary;
  },
});
