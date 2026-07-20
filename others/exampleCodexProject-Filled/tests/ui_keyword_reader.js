'use strict';

const fs = require('fs');
const path = require('path');
const { chromium } = require('@playwright/test');
const { WaitEnforcedCaptureRunner } = require('/workspace/.codex/skills/validation/playwright-testing-qa/scripts/wait_enforced_capture_runner.js');

const runId = 'run-20260720-03';
const scenario = 'automatic_keyword_pdf_reader';
const root = path.join('artifacts', 'ui', runId);
for (const folder of ['screenshots', 'traces', 'videos', 'logs']) fs.mkdirSync(path.join(root, folder), { recursive: true });
const pages = [
  { page: 1, text: 'Neural networks support memory retrieval in adaptive systems. Additional context fills the first page.' },
  { page: 2, text: 'A second discussion compares neural networks and memory retrieval across architectures.' },
  { page: 3, text: 'References demonstrate neural networks in reproducible scientific workflows.' },
];
const result = (keyword, occurrences) => ({ keyword, count: occurrences.length, pages: occurrences.map(([page, start]) => ({ page, start, snippet: `…${pages[page-1].text}…` })) });
const analysis = {
  matching_mode: 'case-insensitive whole words',
  results: [
    result('Neural Networks', pages.map(page => [page.page, page.text.toLowerCase().indexOf('neural networks')])),
    result('memory retrieval', pages.slice(0,2).map(page => [page.page, page.text.toLowerCase().indexOf('memory retrieval')])),
    result('reinforcement learning', []),
  ],
};
const selectors = { primary_action:'#author-search button[type="submit"]', secondary_action:'.candidate:first-child', work:'.work-card:first-child', find:'#analysis-form button[type="submit"]', match:'.reader-keyword:first-child .reader-match:first-of-type', sidebar:'#sidebar-toggle', back:'#reader-back', status_target:'#reader-status', verification_target:'#reader-layout' };

(async()=>{
  const browser=await chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:1600,height:1000},recordVideo:{dir:path.join(root,'videos'),size:{width:1600,height:1000}}});
  await context.tracing.start({screenshots:true,snapshots:true,sources:true});
  const page=await context.newPage(); const actionLog=[]; const runner=new WaitEnforcedCaptureRunner(page,700,actionLog);
  await page.route('**/api/authors?**',route=>route.fulfill({json:{query:'Reader Author',authors:[{id:'A1',name:'Reader Author',affiliation:'Fixture University',works_count:1,cited_by_count:3,topics:['Document analysis'],provider:'OpenAlex'}]}}));
  await page.route('**/api/authors/A1/works',route=>route.fulfill({json:{author_id:'A1',library_states:{W1:'saved locally'},works:[{id:'W1',title:'Neural Networks and Memory Retrieval',authors:['Reader Author'],year:2026,venue:'Fixture Journal',citation_count:3,citation_source:'OpenAlex',retrieved_at:'2026-07-20T00:00:00Z',pdf:{is_open_access:false,url:null,origin:null}}]}}));
  await page.route('**/api/works/W1/documents',route=>route.fulfill({json:{documents:[{id:'D1',work_id:'W1',display_name:'reader.pdf',origin:'upload',local_path:'fixture',status:'ready',error:null,page_count:3,created_at:'2026-07-20T00:00:00Z'}]}}));
  await page.route('**/api/documents/D1/suggested-keywords',route=>route.fulfill({json:{keywords:['Neural Networks','memory retrieval'],method:'local frequency and repeated phrases'}}));
  await page.route('**/api/documents/D1/analysis',route=>route.fulfill({json:analysis}));
  await page.route('**/api/documents/D1/pages',route=>route.fulfill({json:{document_id:'D1',page_count:3,pages}}));
  await page.goto('http://127.0.0.1:8888',{waitUntil:'networkidle'});
  await page.screenshot({path:path.join(root,'screenshots',`${scenario}_initial.png`),fullPage:true});
  await page.fill('#author-query','Reader Author'); await runner.click(selectors.primary_action,{label:'Search author'});
  await page.locator(selectors.secondary_action).waitFor(); await runner.click(selectors.secondary_action,{label:'Select author'});
  await page.locator(selectors.work).waitFor(); await runner.click(selectors.work,{label:'Select paper'});
  await page.getByText(/Suggested 2 local frequency-based keywords/).waitFor();
  const suggestions=await page.inputValue('#keywords');
  if(suggestions!=='Neural Networks, memory retrieval') throw new Error(`Unexpected suggestions: ${suggestions}`);
  await page.fill('#keywords',`${suggestions}, reinforcement learning`);
  await page.screenshot({path:path.join(root,'screenshots',`${scenario}_in_progress.png`),fullPage:true});
  await runner.click(selectors.find,{label:'Find keywords'});
  await page.locator('#reader-view').waitFor({state:'visible'});
  const geometry=await page.evaluate(()=>{const layout=document.querySelector('#reader-layout').getBoundingClientRect();const preview=document.querySelector('#pdf-preview').getBoundingClientRect();const sidebar=document.querySelector('#reader-sidebar').getBoundingClientRect();return {layout:layout.width,preview:preview.width,sidebar:sidebar.width,previewRatio:preview.width/(preview.width+sidebar.width)};});
  if(geometry.previewRatio<0.70||geometry.previewRatio>0.80) throw new Error(`Reader ratio outside 75/25 tolerance: ${geometry.previewRatio}`);
  if(await page.locator('.pdf-page').count()!==3) throw new Error('Full page set was not rendered');
  await runner.click(selectors.match,{label:'Open highlighted match'});
  const active=await page.locator('mark.active-match').evaluate(element=>({focused:document.activeElement===element,text:element.textContent,visible:Boolean(element.offsetParent)}));
  if(!active.focused||active.text.toLowerCase()!=='neural networks'||!active.visible) throw new Error(`Match navigation failed: ${JSON.stringify(active)}`);
  await runner.click(selectors.sidebar,{label:'Minimize keyword sidebar'});
  if(!(await page.locator('#reader-sidebar').isHidden())) throw new Error('Sidebar did not minimize');
  await runner.click(selectors.sidebar,{label:'Restore keyword sidebar'});
  if(!(await page.locator('#reader-sidebar').isVisible())) throw new Error('Sidebar did not restore');
  await page.screenshot({path:path.join(root,'screenshots',`${scenario}_complete_marked.png`),fullPage:true});
  await page.locator(selectors.verification_target).screenshot({path:path.join(root,'screenshots',`${scenario}_verification_target.png`)});
  await runner.click(selectors.back,{label:'Back to papers'});
  if(!(await page.locator('#workspace').isVisible())||await page.inputValue('#keywords')!==`${suggestions}, reinforcement learning`) throw new Error('Back did not restore editable state');
  const violations=actionLog.slice(1).filter(entry=>entry.delta_from_previous_ms<700); if(violations.length) throw new Error(`Pacing violations: ${violations.length}`);
  fs.writeFileSync(path.join(root,'logs',`${scenario}_action_log.json`),JSON.stringify({selectors,minDelayMs:700,actions:actionLog},null,2));
  fs.writeFileSync(path.join(root,`playwright_capture_${scenario}_report.json`),JSON.stringify({status:'passed',suggestions,edited_keywords:await page.inputValue('#keywords'),pages:3,geometry,match_focus:active,sidebar_minimize_restore:true,back_restored:true,actions:actionLog.length,pacing_violations:0},null,2));
  await context.tracing.stop({path:path.join(root,'traces',`${scenario}_trace.zip`)}); await context.close(); await browser.close();
})().catch(error=>{console.error(error);process.exit(1);});
