'use strict';

const fs = require('fs');
const path = require('path');
const { chromium } = require('@playwright/test');
const { WaitEnforcedCaptureRunner } = require('/workspace/.codex/skills/validation/playwright-testing-qa/scripts/wait_enforced_capture_runner.js');

const runId = 'run-20260720-01';
const scenario = 'author_to_keyword_evidence';
const root = path.join('artifacts', 'ui', runId);
for (const folder of ['screenshots', 'traces', 'videos', 'logs']) fs.mkdirSync(path.join(root, folder), { recursive: true });

const selectors = {
  primary_action: '#author-search button[type="submit"]',
  candidate: '.candidate',
  work: '.work-card',
  file_input: '#pdf-file',
  upload_action: '#upload-form button[type="submit"]',
  final_action: '#analysis-form button[type="submit"]',
  status_target: '#analysis-status',
  verification_target: '#evidence-viewer',
  keyword_result: '.keyword-button',
};

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, recordVideo: { dir: path.join(root, 'videos'), size: { width: 1440, height: 1000 } } });
  await context.tracing.start({ screenshots: true, snapshots: true, sources: true });
  const page = await context.newPage();
  const actionLog = [];
  const runner = new WaitEnforcedCaptureRunner(page, 700, actionLog);
  let uploaded = false;

  await page.route('**/api/authors?**', route => route.fulfill({ json: { query: 'Ada Example', authors: [{ id: 'A123', name: 'Ada Example', affiliation: 'Example University', works_count: 12, cited_by_count: 99, topics: ['Machine Learning'], provider: 'OpenAlex' }] } }));
  await page.route('**/api/authors/A123/works', route => route.fulfill({ json: { author_id: 'A123', works: [{ id: 'W123', title: 'Evidence by Page', authors: ['Ada Example'], year: 2025, venue: 'Journal of Examples', citation_count: 42, citation_source: 'OpenAlex', retrieved_at: '2026-07-20T00:00:00Z', source_url: 'https://example.org/work', pdf: { is_open_access: false, url: null, origin: null } }] } }));
  await page.route('**/api/works/W123/documents', route => route.fulfill({ json: { documents: uploaded ? [{ id: 'D123', work_id: 'W123', display_name: 'evidence.pdf', origin: 'upload', local_path: 'fixture', status: 'ready', error: null, page_count: 2, created_at: '2026-07-20T00:00:00Z' }] : [] } }));
  await page.route('**/api/documents/upload', route => { uploaded = true; route.fulfill({ json: { document: { id: 'D123', status: 'ready' } } }); });
  await page.route('**/api/documents/D123/analysis', route => route.fulfill({ json: { matching_mode: 'case-insensitive whole words', results: [{ keyword: 'evidence', count: 2, pages: [{ page: 1, snippet: 'Evidence appears in this reproducible result.', start: 0 }, { page: 2, snippet: 'A second evidence location confirms the count.', start: 9 }] }] } }));

  await page.goto(process.env.BASE_URL || 'http://127.0.0.1:8888', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(root, 'screenshots', `${scenario}_initial.png`), fullPage: true });
  await page.fill('#author-query', 'Ada Example');
  await runner.click(selectors.primary_action, { label: 'Search authors' });
  await page.locator(selectors.candidate).waitFor();
  await runner.click(selectors.candidate, { label: 'Select author candidate' });
  await page.locator(selectors.work).waitFor();
  await runner.click(selectors.work, { label: 'Select scholarly work' });
  await page.screenshot({ path: path.join(root, 'screenshots', `${scenario}_in_progress.png`), fullPage: true });
  await page.setInputFiles(selectors.file_input, 'tests/fixtures/evidence.pdf');
  await runner.click(selectors.upload_action, { label: 'Upload authorized PDF', uploadInitiating: true });
  await page.locator('#keywords').waitFor({ state: 'visible' });
  await page.fill('#keywords', 'evidence');
  await runner.click(selectors.final_action, { label: 'Analyze keywords' });
  await page.locator(selectors.keyword_result).waitFor();
  await runner.click(selectors.keyword_result, { label: 'Open page evidence' });
  await page.getByText('Page 1 · Match 1 of 2').waitFor();
  await page.screenshot({ path: path.join(root, 'screenshots', `${scenario}_complete_marked.png`), fullPage: true });
  await page.locator(selectors.verification_target).screenshot({ path: path.join(root, 'screenshots', `${scenario}_verification_target.png`)});

  const violations = actionLog.slice(1).filter(entry => entry.delta_from_previous_ms < 700);
  if (violations.length) throw new Error(`Click pacing violations: ${violations.length}`);
  fs.writeFileSync(path.join(root, 'logs', `${scenario}_action_log.json`), JSON.stringify({ selectors, minDelayMs: 700, actions: actionLog }, null, 2));
  fs.writeFileSync(path.join(root, `playwright_capture_${scenario}_report.json`), JSON.stringify({ status: 'passed', expected_status: 'Analysis complete', actions: actionLog.length, pacing_violations: violations.length, verification_text: await page.locator(selectors.verification_target).innerText() }, null, 2));
  await context.tracing.stop({ path: path.join(root, 'traces', `${scenario}_trace.zip`) });
  await context.close();
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
