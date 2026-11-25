const $ = selector => document.querySelector(selector)
const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[character]))
const helmet = '<svg class="action-helmet" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 11V9C5 1 27 1 27 9V24L22 29H10L5 24V11ZM5 11H27L25 19H7L5 11ZM10 23H22M11 26H21M2 12H5V22H2ZM27 12H30V22H27Z"/></svg>'
const key = 'icaic-free-v1'
let saved
try { saved = JSON.parse(localStorage.getItem(key)) } catch {}
let record = saved && Array.isArray(saved.attempts) ? saved : {profile:'Angelo', attempts:[]}
if (!['Angelo','Colin','Anna'].includes(record.profile)) record.profile = 'Angelo'
const state = {tasks:[], hard:null, repository:'', cloudGrading:false}
const persist = () => {
  try { localStorage.setItem(key, JSON.stringify(record)) } catch { toast('Browser storage is unavailable. Export your history before leaving.') }
}
const toast = message => {
  $('#toast').textContent = message
  $('#toast').classList.add('show')
  setTimeout(() => $('#toast').classList.remove('show'), 5000)
}
const taskById = id => state.tasks.find(task => task.id === id) || state.hard?.tasks.find(task => task.id === id)
const attemptFor = task => record.attempts.find(attempt => attempt.task === task && attempt.name === record.profile)
const icon = id => ({admissions:'P(y|x)', unet:'[ H × W ]', catacombs:'S → A', basketball:'P(shot)', 'real-fake':'[ RGB ]', pendulum:'θ(t)'}[id])
const repo = () => `https://github.com/${state.repository}`
const localGradingGuide = () => `${repo()}#grade-an-original-task-locally`
const download = (value, filename) => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], {type:'application/json'}))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function navLink(href, label, active) {
  return `<a href="${href}"${active ? ' class="active" aria-current="page"' : ''}>${esc(label)}</a>`
}

function shell(content, page='home') {
  return `<div class="shell"><aside class="sidebar">
    <div class="brand"><div class="brandmark">P</div><div><strong>Practice Room</strong><span>ICAIC / TEAM PREPARATION</span></div></div>
    <nav aria-label="Practice room">${navLink('#home', 'Practice desk', page === 'home')}${navLink('#hard', 'Hard?', page === 'hard')}${navLink('#progress', 'Progress', page === 'progress')}<a href="${repo()}" target="_blank" rel="noopener">Team repository ${helmet}</a></nav>
    <div class="sidebar-bottom"><label for="profile">Your local profile</label><select id="profile" class="profile-picker">${['Angelo','Colin','Anna'].map(name=>`<option ${name===record.profile?'selected':''}>${name}</option>`).join('')}</select><p class="small" style="margin-top:12px">This profile keeps your timer and notes separate in this browser.</p></div></aside>
    <main class="main"><div class="topbar"><strong>Team practice</strong></div><div id="page">${content}</div></main></div>`
}

function home() {
  return `<section class="hero"><div><div class="eyebrow">Your practice desk, ${esc(record.profile)}</div><h1>Practice Room</h1><p>Open a task, check the files, and start a timed or untimed attempt.</p></div><div class="home-hard"><h2>Hard?</h2><p>Browse collegiate and research competition problems with their own files, rules, and evaluators.</p><a class="btn" href="#hard">Open the list ${helmet}</a></div></section><div class="section-head"><h2>Original practice tasks</h2><p>Original pilot: 01 to 03 · China set: 04 to 06</p></div><div class="task-grid">${state.tasks.map(task=>`<article class="task-card"><div class="task-art"><span class="large-number">${task.number}</span><span class="art-symbol">${icon(task.id)}</span></div><div class="task-body"><span class="eyebrow">${task.code} / ${esc(task.division)}</span><h3>${esc(task.title)}</h3><p>${esc(task.description)}</p><div class="task-meta"><span>${task.duration} min suggested</span><span>${attemptFor(task.id)?'Work saved locally':'Ready to start'}</span></div><a class="task-action" href="#task=${task.id}">Open task ${helmet}</a></div></article>`).join('')}</div>`
}

function attemptPanel(task) {
  const attempt = attemptFor(task.id)
  if (!attempt || attempt.closed) return `<section class="panel"><div class="eyebrow">A focused attempt</div><h3>Give yourself a starting point.</h3><p>Learning mode welcomes help. Independent mode gives you a personal timer. Save your result and notes when you finish.</p><form id="start-form"><label class="field">Mode<select name="mode"><option value="learning">Learning</option><option value="independent">Independent</option></select></label><label class="field">Time budget in minutes<input name="minutes" type="number" min="15" max="360" value="${task.duration}"></label><button class="btn wide">Start an attempt ${helmet}</button></form><p class="small muted" style="margin-top:16px">${attempt?'Your finished attempt is saved in local history. ':''}The timer and notes stay in this browser. Download a backup from Progress.</p></section>`
  return `<section class="panel"><div class="eyebrow">${esc(attempt.mode)} attempt</div><h3>Keep a result you trust.</h3><div class="attempt-stat"><span>${attempt.mode==='independent'?'Time remaining':'Time elapsed'}</span><strong data-timer class="mono"></strong></div><p>Save your solution and result before finishing the attempt.</p><button class="btn wide" data-action="finish">Finish this attempt</button><p class="small muted" style="margin-top:16px">The browser clock tracks your practice time. Grading takes place separately.</p></section>`
}

function workspace(task) {
  return `<section class="panel"><h2>Your notebook is ready.</h2><ol><li>Open the notebook below and choose File, Save a copy in Drive.</li><li>Run setup once. It downloads the verified task pack into your runtime.</li><li>Work through the starter cells. In Colab's Files pane, open the task folder printed by setup to edit submission.py or submission_model.py when needed.</li><li>Run Download for the hub. Keep the exported ZIP and your notebook, then open <a href="#task=${task.id}&tab=submissions">Grading &amp; notes</a>.</li></ol><div class="free-actions"><a class="btn" href="${task.colab}" target="_blank" rel="noopener">Open in Colab ${helmet}</a><a class="btn secondary" href="packs/${task.id}.zip" download>Download task pack ${helmet}</a></div><p class="small muted">Free Colab runtimes can disconnect. Save your notebook in Drive and download your ZIP before leaving.</p></section><div class="section-head"><h2>Supplied files</h2></div><section class="panel"><div class="file-list">${task.files.map(file=>`<div class="file-row"><a class="mono" href="packs/${task.id}/${encodeURIComponent(file.name)}" download>${esc(file.name)}</a><span class="muted">${(file.bytes/1024).toFixed(0)} KB ${helmet}</span></div>`).join('')}</div></section>`
}

function notesPanel(attempt) {
  if (!attempt) return '<p class="small muted notes-panel">Start an attempt to keep notes and a result with your practice history.</p>'
  return `<section class="panel notes-panel"><h3><label for="notes">Your working notes</label></h3><p class="small muted">Record your split, metric, result, and next experiment. Notes are saved in this browser.</p><textarea id="notes" class="local-note" maxlength="12000">${esc(attempt.notes || '')}</textarea><p class="status-line" id="note-status">Saved locally</p></section>`
}

function submit(task) {
  const attempt = attemptFor(task.id)
  if (!state.cloudGrading) {
    const zipName = task.extension === '.zip' ? task.upload_name : 'hub-upload.zip'
    return `<section class="panel prose"><h2>Score your saved result</h2><p>Follow the local grading guide to set up the grader on Linux. From the repository folder, run the command below with the ZIP you exported from Colab.</p><pre><code>uv run --frozen python cloud_grade.py --local ${esc(task.id)} /path/to/${esc(zipName)}</code></pre><p>The grader reports validation and final practice results. For an independent attempt, finish your timer before running it.</p><div class="free-actions"><a class="btn" href="${localGradingGuide()}" target="_blank" rel="noopener">Open local grading guide ${helmet}</a></div></section>${notesPanel(attempt)}`
  }
  const body = `### Task\n\n${task.id}\n\n### Participant\n\n${record.profile}\n\n### Practice mode\n\n${attempt?.mode==='independent'?'Independent':'Learning'}\n\n### Submission\n\nDrag your saved ZIP here and wait for its attachment link.\n\n### Reflection\n\nDescribe your experiment, development score, time spent, and next step.`
  const url = `${repo()}/issues/new?title=${encodeURIComponent(`[Submission] ${record.profile} / ${task.title}`)}&labels=submission&body=${encodeURIComponent(body)}`
  return `<section class="panel"><h2>Submit a saved result.</h2><ol><li>Finish your independent attempt first, if using a timer.</li><li>Run the final Download for the hub cell in Colab. ${task.extension==='.zip'?'Keep submission.zip.':'Keep hub-upload.zip. It contains only '+esc(task.upload_name)+'.'}</li><li>Open the submission form below. Sign in with your own GitHub account.</li><li>Replace the attachment instruction with your ZIP by dragging it into the text box. Wait until its link appears, add your reflection, then create the issue.</li><li>Follow the issue for its grading receipt. Allow several minutes for the CPU environment to start.</li></ol><div class="free-actions"><a class="btn" href="${url}" target="_blank" rel="noopener">Open submission form ${helmet}</a><a class="btn secondary" href="${repo()}/issues?q=is%3Aissue+label%3Asubmission" target="_blank" rel="noopener">See submitted work ${helmet}</a></div><div class="notice">Owners and repository collaborators are graded automatically. Until Colin or Anna accepts a collaborator invitation, the owner can approve a submission by adding the grade label. Changing an existing issue does not start a new grade. Open a new submission for each saved version.</div><p class="small muted">Every cloud submission receives validation and final practice results. Evaluation fixtures and submitted files are public. Worked teaching solutions stay in the coach's separate folder.</p></section>${attempt?`<section class="panel" style="margin-top:20px"><h3>Your working notes</h3><p class="small muted">Saved in this browser. Include your split, result, and next useful experiment.</p><textarea id="notes" class="local-note" maxlength="12000">${esc(attempt.notes||'')}</textarea><p class="status-line" id="note-status">Saved locally</p></section>`:''}`
}

function taskPage(task, tab) {
  const content = tab==='workspace'?workspace(task):tab==='submissions'?submit(task):`<div class="notice">${esc(task.adaptation)}</div><section class="panel prose">${task.statement}</section><div class="free-actions"><a class="btn secondary" href="${task.source}" target="_blank" rel="noopener">Original statement ${helmet}</a><a class="btn secondary" href="packs/${task.id}/Statement.md" download>Download practice statement ${helmet}</a></div>`
  return `<a class="back" href="#home">${helmet} Practice desk</a><div class="task-header"><div><div class="eyebrow">${task.code} / ${esc(task.division)}</div><h1>${esc(task.title)}</h1><p>${esc(task.subtitle)}</p></div><span class="tag">${esc(task.kind)}</span></div><nav class="tabs" aria-label="Task navigation">${[['overview','The task'],['workspace','Notebook & files'],['submissions','Grading & notes']].map(([id,title])=>navLink(`#task=${task.id}&tab=${id}`,title,tab===id)).join('')}</nav><div class="task-layout"><div>${content}</div><aside>${attemptPanel(task)}</aside></div>`
}

function progress() {
  const attempts = record.attempts.filter(attempt=>attempt.name===record.profile)
  const independent = attempts.some(attempt=>!attempt.closed && attempt.mode==='independent')
  const shared = state.cloudGrading ? `<div class="section-head"><h2>Recent shared grading receipts</h2>${independent?'':'<button class="btn secondary" data-action="refresh-board">Refresh board</button>'}</div><section class="panel" id="shared-board">${independent?'<p>Finish your independent attempt before viewing peer results here.</p>':'<p class="muted">Choose Refresh board to load receipts from recent submissions.</p>'}</section><p class="small muted notes-panel"><a href="${repo()}/issues?q=is%3Aissue+label%3Asubmission" target="_blank" rel="noopener">All submission requests on GitHub ${helmet}</a></p>` : ''
  return `<div class="task-header"><div><h1>Progress and submissions</h1><p>Your attempts and notes stay in this browser. Save a backup to take them with you.</p></div></div><section class="panel"><h2>Your local history</h2>${attempts.length?attempts.map(attempt=>`<div class="board-row"><a href="#task=${encodeURIComponent(attempt.task)}&tab=submissions">${esc(taskById(attempt.task)?.title||attempt.task)} ${helmet}</a><p class="small muted">${esc(attempt.mode)} · ${new Date(attempt.started).toLocaleString()} · ${attempt.closed?'Finished':'In progress'}</p><p class="small">${esc(attempt.notes||'No notes saved yet.')}</p></div>`).join(''):'<p class="muted">Start an attempt on a task page to keep your first record.</p>'}<div class="free-actions"><button class="btn secondary" data-action="export">Download history backup</button><label class="btn secondary">Import backup<input type="file" id="import-history" accept=".json" hidden></label></div></section>${shared}`
}

function updateTimer() {
  const params = new URLSearchParams(location.hash.slice(1))
  const attempt = attemptFor(params.get('task'))
  const output = $('[data-timer]')
  if (!output || !attempt) return
  const seconds = Math.max(0, Math.floor((attempt.mode==='independent'?attempt.deadline-Date.now():Date.now()-attempt.started)/1000))
  output.textContent = `${Math.floor(seconds/3600)}:${String(Math.floor(seconds/60)%60).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`
  if (attempt.mode==='independent' && seconds===0 && !attempt.closed) {
    attempt.closed = Date.now()
    persist()
    render()
    toast('Your time budget ended. Save your work and follow the task’s grading instructions.')
  }
}

async function loadBoard() {
  const panel = $('#shared-board')
  if (!panel) return
  panel.textContent = 'Loading grading receipts...'
  try {
    const cacheKey = 'icaic-board-cache'
    let cached
    try { cached = JSON.parse(localStorage.getItem(cacheKey)) } catch {}
    let receipts
    if (cached && cached.at > Date.now()-300000) receipts = cached.receipts
    else {
      const response = await fetch(`https://api.github.com/repos/${state.repository}/issues?labels=submission&state=all&per_page=20&sort=updated`)
      if (!response.ok) throw new Error('GitHub is temporarily unavailable or its public request limit was reached. Open the submission list on GitHub to see results.')
      const issues = await response.json()
      receipts = []
      const requests = await Promise.allSettled(issues.filter(issue=>issue.comments && !issue.pull_request).map(async issue=>{
        const commentsResponse = await fetch(`${issue.comments_url}?per_page=100`)
        if (!commentsResponse.ok) throw new Error('Could not load some receipts. See the GitHub submission list.')
        const comments = await commentsResponse.json()
        for (const comment of comments) {
          if (comment.user.login!=='github-actions[bot]' || !comment.body.includes('<!-- icaic-grade-v1 -->')) continue
          const match = comment.body.match(/```json\s*([\s\S]*?)```/)
          if (!match) continue
          const receipt = JSON.parse(match[1])
          if (receipt.schema==='icaic-grade-v1') receipts.push({...receipt, url:issue.html_url, number:issue.number})
        }
      }))
      if (requests.some(result=>result.status==='rejected')) throw new Error('Some receipts could not be loaded. Open the GitHub submission list for the complete record.')
      try { localStorage.setItem(cacheKey, JSON.stringify({at:Date.now(),receipts})) } catch {}
    }
    if (!$('#shared-board')) return
    panel.innerHTML = receipts.length?receipts.map(receipt=>`<div class="board-row"><div class="eyebrow">${esc(receipt.name||'Submission')} / ${esc(taskById(receipt.task)?.title||receipt.task||'Needs repair')}</div><h3 style="margin-top:8px">${esc(receipt.status==='graded'?receipt.validation.display:'Needs repair')}</h3><p class="small">${receipt.final?'Final practice result: '+esc(receipt.final.display):esc(receipt.error||'')}</p><a class="small" href="${esc(receipt.url)}" target="_blank" rel="noopener">Receipt #${receipt.number} ${helmet}</a></div>`).join(''):'<p>No graded submissions yet. Your first submitted ZIP will appear here after the grader finishes. Requests awaiting approval remain visible in the GitHub submission list.</p>'
  } catch (error) { if ($('#shared-board')) panel.textContent=error.message }
}

function render() {
  const params = new URLSearchParams(location.hash.slice(1))
  const task = taskById(params.get('task'))
  const tab = ['workspace', 'submissions'].includes(params.get('tab')) ? params.get('tab') : 'overview'
  let content = home()
  let page = 'home'
  if (task?.access) {
    page = 'hard'
    content = hardTaskPage(task, tab)
  } else if (task) content = taskPage(task, tab)
  else if (location.hash === '#hard' || location.hash === '#aic') {
    page = 'hard'
    content = location.hash === '#aic' ? aicPage() : hardList()
  } else if (location.hash === '#progress') {
    page = 'progress'
    content = progress()
  } else if (params.has('task')) {
    content = '<section class="panel"><h1>Task unavailable</h1><p>Find it on the <a href="#home">Practice desk</a> or in <a href="#hard">Hard?</a>.</p></section>'
  }
  $('#app').innerHTML = shell(content, page)
  $('#profile').addEventListener('change', event=>{record.profile=event.target.value;persist();render()})
  $('#start-form')?.addEventListener('submit', event=>{
    event.preventDefault()
    const form = new FormData(event.target)
    const now = Date.now()
    record.attempts.unshift({id:crypto.randomUUID(), name:record.profile, task:task.id, mode:form.get('mode'), started:now, deadline:now+Number(form.get('minutes'))*60000, closed:null, notes:''})
    persist()
    render()
  })
  $('[data-action=finish]')?.addEventListener('click',()=>{attemptFor(task.id).closed=Date.now();persist();render();toast('Attempt saved. Open the grading tab for the next step.')})
  $('#notes')?.addEventListener('input',event=>{attemptFor(task.id).notes=event.target.value;persist();$('#note-status').textContent='Saved locally'})
  $('[data-action=export]')?.addEventListener('click',()=>download(record,'ICAIC-practice-history.json'))
  $('#import-history')?.addEventListener('change',async event=>{
    try {
      const file = event.target.files[0]
      if (!file || file.size>2000000) throw new Error('Choose a history backup below 2 MB')
      const data = JSON.parse(await file.text())
      if (!Array.isArray(data.attempts) || data.attempts.length>1000 || data.attempts.some(attempt=>!taskById(attempt.task)||!['Angelo','Colin','Anna'].includes(attempt.name)||!Number.isFinite(attempt.started)||!Number.isFinite(attempt.deadline)||!['learning','independent'].includes(attempt.mode))) throw new Error('Choose a valid practice history backup')
      const known = new Set(record.attempts.map(attempt=>attempt.id))
      record.attempts.push(...data.attempts.filter(attempt=>!known.has(attempt.id)))
      persist()
      render()
      toast('History imported. Existing attempts were kept.')
    } catch (error) {toast(error.message)}
  })
  $('[data-action=refresh-board]')?.addEventListener('click',loadBoard)
  updateTimer()
}

addEventListener('hashchange', () => {
  if (!state.repository) return
  render()
  window.scrollTo(0, 0)
  const heading = $('#page h1')
  if (heading) {
    heading.tabIndex = -1
    heading.focus({preventScroll: true})
  }
})
setInterval(updateTimer,1000)
async function loadJson(path) {
  const response = await fetch(path, {cache: 'no-cache'})
  if (!response.ok) throw new Error('The task library could not be loaded.')
  return response.json()
}

async function loadCatalog() {
  const [original, hard] = await Promise.allSettled([loadJson('tasks.json'), loadJson('hard.json')])
  if (original.status !== 'fulfilled' || !Array.isArray(original.value.tasks)) {
    $('#app').innerHTML = '<main class="initial"><h1>The practice room could not load</h1><p>Check your connection and <a href="">reload the page</a>.</p></main>'
    return
  }
  state.repository = original.value.repository
  state.tasks = original.value.tasks
  state.cloudGrading = original.value.cloudGrading === true
  if (hard.status === 'fulfilled' && Array.isArray(hard.value.tasks) && hard.value.aic) state.hard = hard.value
  render()
}

loadCatalog()
