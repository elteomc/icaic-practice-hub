const accessLabels = {
  local: 'Local evaluator',
  organizer: 'Organizer account',
  reference: 'Organizer data required'
}

function hardStatus(task) {
  return `<span class="access-label ${esc(task.access)}">${esc(accessLabels[task.access])}</span>`
}

function resourceLink(resource, primary = false) {
  return `<a class="btn${primary ? '' : ' secondary'}" href="${esc(resource.url)}" target="_blank" rel="noopener noreferrer">${esc(resource.label)} ${helmet}</a>`
}

function hardCard(task) {
  return `<article class="hard-card">
    <div>${hardStatus(task)}<p class="eyebrow">${esc(task.source)}</p></div>
    <div><h3>${esc(task.title)}</h3><p>${esc(task.description)}</p></div>
    <div class="hard-card-end"><span>${esc(task.division)}</span><a class="task-action" href="#task=${esc(task.id)}" aria-label="Open ${esc(task.title)}">Open task ${helmet}</a></div>
  </article>`
}

function hardList() {
  if (!state.hard) return '<section class="panel"><h1>Hard?</h1><p>The task list could not be loaded. <a href="">Reload the practice room</a>.</p></section>'
  const {aic, tasks} = state.hard
  return `<div class="task-header"><div><div class="eyebrow">Practice catalog</div><h1>Hard?</h1><p>Read the brief, check the files and evaluator, then start the clock.</p></div></div>
    <section aria-labelledby="hard-tasks-title"><div class="section-head"><h2 id="hard-tasks-title">Individual tasks</h2></div>
      <div class="hard-grid">${tasks.filter(task => !task.series).map(hardCard).join('')}</div></section>
    <section class="hard-collection" aria-labelledby="aic-title"><div><p class="eyebrow">Competition collection · China</p><h2 id="aic-title">${esc(aic.title)}</h2><p>${esc(aic.description)}</p></div><a class="btn secondary" href="#aic">Open collection ${helmet}</a></section>`
}

function aicPage() {
  if (!state.hard) return hardList()
  const {aic, tasks} = state.hard
  return `<a class="back" href="#hard">${helmet} Hard?</a>
    <div class="task-header"><div><div class="eyebrow">Competition collection · China</div><h1>${esc(aic.title)}</h1><p>${esc(aic.description)}</p></div></div>
    <p class="notice">The English briefs link to the official Chinese rules. Confirm organizer data access before planning a scored attempt.</p>
    <section aria-labelledby="aic-tasks-title"><div class="section-head"><h2 id="aic-tasks-title">2026 Algorithm Challenge</h2></div>
      <div class="hard-grid">${tasks.filter(task => task.series === 'aic').map(hardCard).join('')}</div></section>
    <section class="panel hard-tracks"><h2>All six track archives</h2><p>Follow the official indexes for additional tasks, project requirements and any available data.</p>
      <ul class="track-grid">${aic.tracks.map(track => `<li><a href="${esc(track.url)}" target="_blank" rel="noopener noreferrer">${esc(track.label)} ${helmet}</a></li>`).join('')}</ul>
      <div class="free-actions">${resourceLink(aic.archive)}${resourceLink(aic.eligibility)}</div></section>`
}

function hardOverview(task) {
  return `<section class="panel prose hard-panel"><h2>Objective</h2><p>${esc(task.objective)}</p>
    <h3>What to hand in</h3><p>${esc(task.deliverable)}</p>
    <h3>Rules for this attempt</h3><ul>${task.rules.map(rule => `<li>${esc(rule)}</li>`).join('')}</ul>
    <div class="free-actions">${resourceLink(task.statement, true)}<a class="btn secondary" href="#task=${esc(task.id)}&tab=workspace">Check files and setup ${helmet}</a></div></section>`
}

function hardWorkspace(task) {
  return `<section class="panel prose hard-panel"><h2>Files</h2><dl class="hard-files">${task.files.map(file => `<div><dt>${esc(file.name)}</dt><dd>${esc(file.description)}</dd></div>`).join('')}</dl>
    <div class="free-actions">${task.resources.map((resource, index) => resourceLink(resource, index === 0)).join('')}</div>
    <h3>Before starting the clock</h3><ol>${task.setup.map(step => `<li>${esc(step)}</li>`).join('')}</ol></section>`
}

function hardEvaluation(task) {
  const tool = task.localTool
  return `<section class="panel prose hard-panel"><h2>How it is graded</h2><p class="hard-metric">${esc(task.metric)}</p><p>${esc(task.grading)}</p>
    <h3>How to practice the evaluation</h3><p>${esc(task.rehearsal)}</p>
    ${tool ? `<p>${esc(tool.description)}</p><pre><code>${esc(tool.command)}</code></pre>` : ''}
    ${task.sample ? `<h3>Example output shape</h3><pre><code>${esc(task.sample)}</code></pre>` : ''}
    <div class="free-actions">${resourceLink(task.evaluator, true)}${tool ? `<a class="btn secondary" href="${esc(tool.url)}" download>${esc(tool.label)} ${helmet}</a>` : ''}</div></section>${notesPanel(attemptFor(task.id))}`
}

function hardTaskPage(task, tab) {
  const tabs = [['overview', 'The task'], ['workspace', 'Files & setup'], ['submissions', 'Grading & notes']]
  const content = tab === 'workspace' ? hardWorkspace(task) : tab === 'submissions' ? hardEvaluation(task) : hardOverview(task)
  return `<a class="back" href="${task.series === 'aic' ? '#aic' : '#hard'}">${helmet} ${task.series === 'aic' ? 'Global Campus collection' : 'Hard?'}</a>
    <div class="task-header"><div><div class="eyebrow">${esc(task.source)} / ${esc(task.division)}</div><h1>${esc(task.title)}</h1><p>${esc(task.description)}</p></div>${hardStatus(task)}</div>
    <p class="notice">${esc(task.accessNote)}</p>
    <nav class="tabs" aria-label="Task navigation">${tabs.map(([id, label]) => navLink(`#task=${task.id}&tab=${id}`, label, id === tab)).join('')}</nav>
    <div class="task-layout"><div>${content}</div><aside><section class="panel hard-session"><h2>Session format</h2><p>${esc(task.timing)}</p></section>${task.duration ? attemptPanel(task) : ''}</aside></div>`
}
