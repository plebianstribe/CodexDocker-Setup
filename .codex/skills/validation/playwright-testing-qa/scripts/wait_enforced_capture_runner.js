'use strict';

const { centerForSelector, markerAt } = require('./click_marker_helper');

class WaitEnforcedCaptureRunner {
  constructor(page, minDelayMs, actionLog) {
    this.page = page;
    this.minDelayMs = minDelayMs;
    this.actionLog = actionLog;
    this.lastClickMs = null;
  }

  async click(selector, options = {}) {
    const now = Date.now();
    let rawDelta = null;
    let waitAppliedMs = 0;

    if (this.lastClickMs !== null) {
      rawDelta = now - this.lastClickMs;
      if (rawDelta < this.minDelayMs) {
        waitAppliedMs = this.minDelayMs - rawDelta;
        await this.page.waitForTimeout(waitAppliedMs);
      }
    }

    const coords = await centerForSelector(this.page, selector);
    await markerAt(this.page, coords.x, coords.y, options.label || selector);

    await this.page.click(selector);
    const timestampMs = Date.now();
    const effectiveDelta = this.lastClickMs === null ? null : timestampMs - this.lastClickMs;

    const entry = {
      selector,
      x: coords.x,
      y: coords.y,
      label: options.label || selector,
      upload_initiating: Boolean(options.uploadInitiating),
      timestamp: new Date(timestampMs).toISOString(),
      delta_from_previous_ms: effectiveDelta,
      raw_delta_before_wait_ms: rawDelta,
      wait_applied_ms: waitAppliedMs,
      ris_path: options.risPath || null,
    };

    this.actionLog.push(entry);
    this.lastClickMs = timestampMs;
    return entry;
  }
}

module.exports = {
  WaitEnforcedCaptureRunner,
};
