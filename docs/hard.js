const accessLabels = {
  local: 'Local evaluator',
  organizer: 'Organizer account',
  reference: 'Organizer data required',
  worksheet: 'Self-contained',
  validation: 'Practice scoring',
  hidden: 'Hidden-test scoring',
  review: 'Manual review',
  guided: 'Guided exercise',
  samples: 'Sample tests'
}

const practiceLists = {
  ez: {label: 'ez', description: 'Quick warm-ups and approachable first baselines.'},
  realeyes: {label: 'realeyes', description: 'Easy and medium tasks that reward a problem-specific observation or technique.'},
  o7: {label: 'O7', description: 'Collegiate and research competition problems.'}
}

const isEzTask = id => state.practice?.ez.some(group => group.tasks.includes(id))
const practiceHint = id => state.practice?.realeyes[id]

function taskOrigin(task, via) {
  if (task.series === 'aic') return 'aic'
  if (state.hard?.tasks.includes(task)) return 'o7'
  if (via === 'ez' && isEzTask(task.id)) return 'ez'
  if (via === 'realeyes' && practiceHint(task.id)) return 'realeyes'
  if (state.tasks.includes(task)) return 'home'
  return isEzTask(task.id) ? 'ez' : 'realeyes'
}

function taskLink(task, tab, origin) {
  const params = new URLSearchParams({task: task.id})
  if (tab) params.set('tab', tab)
  if (origin === 'ez' || origin === 'realeyes') params.set('via', origin)
  return `#${params}`
}

function taskBack(origin) {
  const label = practiceLists[origin]?.label ?? (origin === 'aic' ? 'Global Campus collection' : 'Practice desk')
  return `<a class="back" href="#${origin}">${helmet} ${label}</a>`
}

function taskHint(task) {
  const hint = practiceHint(task.id)
  return hint ? `<details class="practice-hint"><summary>Optional hint</summary><p>${esc(hint)}</p></details>` : ''
}

function taskStatus(task) {
  const access = task.access ?? 'local'
  return `<span class="access-label ${esc(access)}">${esc(accessLabels[access])}</span>`
}

function resourceLink(resource, primary = false) {
  return `<a class="btn${primary ? '' : ' secondary'}" href="${esc(resource.url)}" target="_blank" rel="noopener noreferrer">${esc(resource.label)} ${helmet}</a>`
}

function catalogCard(task, origin) {
  const source = task.source_name ?? task.source
  return `<article class="hard-card" data-practice-task="${esc(`${task.title} ${source} ${task.division} ${task.description} ${accessLabels[task.access ?? 'local']}`)}">
    <div>${taskStatus(task)}<p class="eyebrow">${esc(source)}</p></div>
    <div><h3>${esc(task.title)}</h3><p>${esc(task.description)}</p></div>
    <div class="hard-card-end"><span>${esc(task.division)}</span><a class="task-action" href="${esc(taskLink(task, null, origin))}" aria-label="Open ${esc(task.title)}">Open task ${helmet}</a></div>
  </article>`
}

function listUnavailable(label) {
  return `<section class="panel"><h1>${label}</h1><p>The task list could not be loaded. <a href="">Reload the practice room</a>.</p></section>`
}

function practiceList(name) {
  const {label, description} = practiceLists[name]
  if (!state.practice) return listUnavailable(label)
  const groups = name === 'ez' ? state.practice.ez : [{tasks: Object.keys(state.practice.realeyes)}]
  const total = groups.reduce((sum, group) => sum + group.tasks.length, 0)
  return `<div class="task-header"><div><h1>${label}</h1><p>${description}</p></div></div>
    <div class="catalog-search"><label for="catalog-search">Find a task</label><input id="catalog-search" type="search" placeholder="Search by title, topic or contest"><p id="catalog-count" role="status">${total} tasks</p></div>
    <div id="practice-cards">${groups.map(group => `<section data-practice-group>${group.title ? `<div class="section-head"><h2>${esc(group.title)}</h2></div>` : ''}<div class="hard-grid">${group.tasks.map(id => catalogCard(taskById(id), name)).join('')}</div></section>`).join('')}</div>`
}

function filterPractice(query) {
  const words = query.toLowerCase().trim().split(/\s+/)
  let total = 0
  for (const group of $('#practice-cards').querySelectorAll('[data-practice-group]')) {
    let visible = 0
    for (const card of group.querySelectorAll('[data-practice-task]')) {
      const text = card.dataset.practiceTask.toLowerCase()
      card.hidden = !words.every(word => text.includes(word))
      if (!card.hidden) visible++
    }
    group.hidden = visible === 0
    total += visible
  }
  $('#catalog-count').textContent = total ? `${total} ${total === 1 ? 'task' : 'tasks'}` : 'No matching tasks'
}

function o7List() {
  const {label, description} = practiceLists.o7
  if (!state.hard) return listUnavailable(label)
  const {aic, tasks} = state.hard
  return `<div class="task-header"><div><h1>${label}</h1><p>${description}</p></div></div>
    <section aria-labelledby="hard-tasks-title"><div class="section-head"><h2 id="hard-tasks-title">Individual tasks</h2></div>
      <div class="hard-grid">${tasks.filter(task => !task.series).map(task => catalogCard(task, 'o7')).join('')}</div></section>
    <section class="hard-collection" aria-labelledby="aic-title"><div><p class="eyebrow">Competition collection · China</p><h2 id="aic-title">${esc(aic.title)}</h2><p>${esc(aic.description)}</p></div><a class="btn secondary" href="#aic">Open collection ${helmet}</a></section>`
}

function aicPage() {
  if (!state.hard) return o7List()
  const {aic, tasks} = state.hard
  return `${taskBack('o7')}
    <div class="task-header"><div><div class="eyebrow">Competition collection · China</div><h1>${esc(aic.title)}</h1><p>${esc(aic.description)}</p></div></div>
    <p class="notice">The English briefs link to the official Chinese rules. Confirm organizer data access before planning a scored attempt.</p>
    <section aria-labelledby="aic-tasks-title"><div class="section-head"><h2 id="aic-tasks-title">2026 Algorithm Challenge</h2></div>
      <div class="hard-grid">${tasks.filter(task => task.series === 'aic').map(task => catalogCard(task, 'aic')).join('')}</div></section>
    <section class="panel hard-tracks"><h2>All six track archives</h2><p>Follow the official indexes for additional tasks, project requirements and any available data.</p>
      <ul class="track-grid">${aic.tracks.map(track => `<li><a href="${esc(track.url)}" target="_blank" rel="noopener noreferrer"><span><strong>${esc(track.label)}</strong><small>${esc(track.description)}</small></span>${helmet}</a></li>`).join('')}</ul>
      <div class="free-actions">${resourceLink(aic.archive)}${resourceLink(aic.eligibility)}</div></section>`
}

function briefOverview(task, origin) {
  return `<section class="panel prose hard-panel"><h2>Objective</h2><p>${esc(task.objective)}</p>
    <h3>What to hand in</h3><p>${esc(task.deliverable)}</p>
    <h3>Rules for this attempt</h3><ul>${task.rules.map(rule => `<li>${esc(rule)}</li>`).join('')}</ul>
    <div class="free-actions">${resourceLink(task.statement, true)}<a class="btn secondary" href="${esc(taskLink(task, 'workspace', origin))}">Check files and setup ${helmet}</a></div>${taskHint(task)}</section>`
}

function briefWorkspace(task) {
  return `<section class="panel prose hard-panel"><h2>Files</h2><dl class="hard-files">${task.files.map(file => `<div><dt>${esc(file.name)}</dt><dd>${esc(file.description)}</dd></div>`).join('')}</dl>
    <div class="free-actions">${task.resources.map((resource, index) => resourceLink(resource, index === 0)).join('')}</div>
    <h3>Before starting the clock</h3><ol>${task.setup.map(step => `<li>${esc(step)}</li>`).join('')}</ol></section>`
}

function briefEvaluation(task) {
  const tool = task.localTool
  return `<section class="panel prose hard-panel"><h2>How it is graded</h2><p class="hard-metric">${esc(task.metric)}</p><p>${esc(task.grading)}</p>
    <h3>How to practice the evaluation</h3><p>${esc(task.rehearsal)}</p>
    ${tool ? `<p>${esc(tool.description)}</p><pre><code>${esc(tool.command)}</code></pre>` : ''}
    ${task.sample ? `<h3>Example output shape</h3><pre><code>${esc(task.sample)}</code></pre>` : ''}
    <div class="free-actions">${resourceLink(task.evaluator, true)}${tool ? `<a class="btn secondary" href="${esc(tool.url)}" download>${esc(tool.label)} ${helmet}</a>` : ''}</div></section>${notesPanel(attemptFor(task.id))}`
}

function briefTaskPage(task, tab, origin) {
  const tabs = [['overview', 'The task'], ['workspace', 'Files & setup'], ['submissions', 'Grading & notes']]
  const content = tab === 'workspace' ? briefWorkspace(task) : tab === 'submissions' ? briefEvaluation(task) : briefOverview(task, origin)
  const session = task.timing ? `<section class="panel hard-session"><h2>Session format</h2><p>${esc(task.timing)}</p></section>` : ''
  return `${taskBack(origin)}
    <div class="task-header"><div><div class="eyebrow">${esc(task.source)} / ${esc(task.division)}</div><h1>${esc(task.title)}</h1><p>${esc(task.description)}</p></div>${taskStatus(task)}</div>
    <p class="notice">${esc(task.accessNote)}</p>
    <nav class="tabs" aria-label="Task navigation">${tabs.map(([id, label]) => navLink(taskLink(task, id, origin), label, id === tab)).join('')}</nav>
    <div class="task-layout"><div>${content}</div><aside>${session}${task.duration ? attemptPanel(task) : ''}</aside></div>`
}
