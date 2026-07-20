'use strict';

const fs = require('fs');
const path = require('path');
const { chromium } = require('@playwright/test');
const { WaitEnforcedCaptureRunner } = require('/workspace/.codex/skills/validation/playwright-testing-qa/scripts/wait_enforced_capture_runner.js');

const runId = 'run-20260720-02';
const scenario = 'live_mehul_motani_library';
const root = path.join('artifacts', 'ui', runId);
for (const folder of ['screenshots', 'traces', 'videos', 'logs']) fs.mkdirSync(path.join(root, folder), { recursive: true });
const selectors = {
  primary_action: '#author-search button[type="submit"]',
  secondary_action: '.candidate',
  final_action: '.work-card:first-child',
  status_target: '#works-status',
  verification_target: '#workspace',
};

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, recordVideo: { dir: path.join(root, 'videos'), size: { width: 1440, height: 1000 } } });
  await context.tracing.start({ screenshots: true, snapshots: true, sources: true });
  const page = await context.newPage();
  const actionLog = [];
  const runner = new WaitEnforcedCaptureRunner(page, 700, actionLog);
  await page.goto('http://127.0.0.1:8888', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(root, 'screenshots', `${scenario}_initial.png`), fullPage: true });
  await page.fill('#author-query', 'Mehul Motani');
  await runner.click(selectors.primary_action, { label: 'Search live OpenAlex for Mehul Motani' });
  await page.locator('.candidate', { hasText: 'Mehul Motani' }).first().waitFor({ timeout: 30000 });
  const candidates = await page.locator('.candidate').allTextContents();
  await runner.click('.candidate:first-child', { label: 'Select first exact Mehul Motani candidate' });
  await page.getByText(/works indexed in this author's local library/).waitFor({ timeout: 30000 });
  await page.screenshot({ path: path.join(root, 'screenshots', `${scenario}_in_progress.png`), fullPage: true });
  await page.locator(selectors.final_action).first().waitFor();
  await runner.click(selectors.final_action, { label: 'Open first indexed Mehul Motani paper' });
  await page.locator('#work-detail').waitFor({ state: 'visible' });
  const authorText = await page.locator('#selected-author').innerText();
  const statusText = await page.locator(selectors.status_target).innerText();
  if (!authorText.includes('Mehul Motani')) throw new Error(`Wrong author selected: ${authorText}`);
  if (!statusText.includes('indexed')) throw new Error(`Library index status missing: ${statusText}`);
  await page.screenshot({ path: path.join(root, 'screenshots', `${scenario}_complete_marked.png`), fullPage: true });
  await page.locator(selectors.verification_target).screenshot({ path: path.join(root, 'screenshots', `${scenario}_verification_target.png`) });
  const violations = actionLog.slice(1).filter(entry => entry.delta_from_previous_ms < 700);
  if (violations.length) throw new Error(`Click pacing violations: ${violations.length}`);
  fs.writeFileSync(path.join(root, 'logs', `${scenario}_action_log.json`), JSON.stringify({ selectors, minDelayMs: 700, actions: actionLog }, null, 2));
  fs.writeFileSync(path.join(root, `playwright_capture_${scenario}_report.json`), JSON.stringify({ status: 'passed', query: 'Mehul Motani', author: authorText, works_status: statusText, candidate_count: candidates.length, candidates, actions: actionLog.length, pacing_violations: violations.length }, null, 2));
  await context.tracing.stop({ path: path.join(root, 'traces', `${scenario}_trace.zip`) });
  await context.close();
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
