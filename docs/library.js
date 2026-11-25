const gradeRoutes = {
  local: {title: 'Local evaluator', detail: 'Use the supplied evaluator, notebook, or simulator to score your work.'},
  validation: {title: 'Local validation', detail: 'Use the available labeled data to check a practice result.'},
  samples: {title: 'Samples or answer key', detail: 'Check your work using the sample cases, supplied tests, or answer key.'},
  manual: {title: 'Manual review', detail: 'Use the task rubric or check the written reasoning and output by hand.'},
  judge: {title: 'Organizer judge', detail: 'See the organizer for grading rules and current submission access.'},
  unknown: {title: 'Grading unverified', detail: 'Check the original materials for an evaluator or rubric before starting a scored attempt.'},
  pending: {title: 'Materials pending', detail: 'Confirm access to the task materials before scheduling an attempt.'},
  reference: {title: 'Reference material', detail: 'Follow the individual tasks or exercises for their scoring instructions.'}
}

const entryKinds = {
  task: 'Archived task', paper: 'Paper or assessment', resource: 'Practice resource',
  exercise: 'Practice exercise', lead: 'Unfinished lead', track: 'Organizer track index'
}

const englishMaterials = {
  full: 'Full statement or starter',
  brief: 'English practice brief',
  incomplete: 'English materials incomplete'
}

const library = {index: null, entries: [], loading: false, failed: false}
const matchesLibrary = (route, params) => route === 'catalog' || route.startsWith('catalog&') || params.has('entry')
const libraryPageSize = 24

async function loadLibrary() {
  if (library.loading) return
  library.loading = true
  try {
    const index = await loadJson('catalog/index.json')
    const groups = await Promise.all(index.topics.map(async topic => {
      const entries = await loadJson(`catalog/${topic.id}.json`)
      return entries.map(entry => ({...entry, topic: topic.id}))
    }))
    library.index = index
    library.entries = groups.flat()
  } catch {
    library.failed = true
  } finally {
    library.loading = false
    const route = location.hash.slice(1)
    if (matchesLibrary(route, new URLSearchParams(route))) render()
  }
}

function libraryFilters(params) {
  const topic = params.get('topic')
  const grade = params.get('grade')
  const english = params.get('english')
  return {
    topic: library.index.topics.some(item => item.id === topic) ? topic : '',
    grade: Object.hasOwn(gradeRoutes, grade) ? grade : '',
    english: Object.hasOwn(englishMaterials, english) ? english : '',
    q: (params.get('q') ?? '').trim().slice(0, 100),
    page: Math.max(1, Number.parseInt(params.get('page'), 10) || 1)
  }
}

function libraryLink(filters, id) {
  const params = new URLSearchParams()
  if (id) params.set('entry', id)
  for (const key of ['topic', 'grade', 'english', 'q']) if (filters[key]) params.set(key, filters[key])
  if (filters.page > 1) params.set('page', filters.page)
  const suffix = params.toString()
  return id ? `#${suffix}` : suffix ? `#catalog&${suffix}` : '#catalog'
}

const libraryTopic = id => library.index.topics.find(topic => topic.id === id)
const libraryCollection = id => library.index.collections[id]
const findText = value => value.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()

function libraryEnglish(entry, brief) {
  const english = entry.english
  if (!english) return ''
  const copy = english.status === 'full' ? '' : englishMaterials[english.status]
  const links = english.links ?? []
  const needsUpload = links.some(link => link.format === 'notebook' && !link.url.startsWith('https://github.com/') && link.url.endsWith('.ipynb'))
  return `<section class="library-english" aria-label="Practice in English"><h3>Practice in English</h3>
    ${copy ? `<p><strong>${copy}</strong></p>` : ''}
    ${english.note ? `<p>${esc(english.note)}</p>` : ''}
    ${english.steps?.length ? `<ol>${english.steps.map(step => `<li>${esc(step)}</li>`).join('')}</ol>` : ''}
    ${brief && english.status === 'brief' ? `<p><a href="${esc(taskLink(brief))}">Open the hub practice brief</a></p>` : ''}
    ${links.length ? `<ul class="library-sources">${links.map(link => {
      const githubNotebook = link.format === 'notebook' && /^https:\/\/github\.com\/[^/]+\/[^/]+\/blob\/(?!HEAD\/).+\.ipynb$/.test(link.url)
      const colab = githubNotebook ? `<a href="${esc(link.url.replace('https://github.com/', 'https://colab.research.google.com/github/'))}" target="_blank" rel="noopener noreferrer">Open in Colab</a>` : ''
      return `<li><a href="${esc(link.url)}" target="_blank" rel="noopener noreferrer">${esc(link.label)}</a> <small>(${esc(link.credit)})</small>${colab ? ` · ${colab}` : ''}</li>`
    }).join('')}</ul>` : ''}
    ${needsUpload ? '<p class="small">Open the downloaded notebook in Jupyter or use File → Open notebook → Upload in Colab.</p>' : ''}
  </section>`
}

function libraryGrades(entry) {
  return `<ul class="library-grades" aria-label="Grading routes">${entry.grades.map(grade => `<li class="access-label ${grade === 'judge' ? 'organizer' : grade}">${gradeRoutes[grade].title}</li>`).join('')}</ul>`
}

function libraryCard(entry, filters) {
  const collection = libraryCollection(entry.collection)
  const brief = taskById(entry.hubTask)
  const description = entry.summary || brief?.description
  const link = esc(libraryLink(filters, entry.id))
  return `<article class="hard-card" data-library-entry="${esc(entry.id)}">
    <p class="eyebrow">${esc(entry.source || collection.title)}${entry.variant ? ` · ${esc(entry.variant)}` : ''}</p>
    <div><h3><a href="${link}">${esc(entry.title)}</a></h3>${description ? `<p>${esc(description)}</p>` : ''}</div>
    <div class="library-card-meta">${libraryGrades(entry)}<p>${esc(libraryTopic(entry.topic).title)}${entry.kind !== 'task' ? ` · ${esc(entryKinds[entry.kind])}` : ''}</p></div>
  </article>`
}

function libraryResults(filters) {
  const words = findText(filters.q).split(/\s+/).filter(Boolean)
  const matches = library.entries.filter(entry => {
    if (filters.topic && entry.topic !== filters.topic) return false
    if (filters.grade && !entry.grades.includes(filters.grade)) return false
    if (filters.english && entry.english?.status !== filters.english) return false
    if (!words.length) return true
    const brief = taskById(entry.hubTask)
    const text = findText([entry.id, entry.title, entry.summary || brief?.description, entry.source, entry.variant, libraryCollection(entry.collection).title].join(' '))
    return words.every(word => text.includes(word))
  })
  const pages = Math.max(1, Math.ceil(matches.length / libraryPageSize))
  const page = Math.min(filters.page, pages)
  const first = (page - 1) * libraryPageSize
  const last = Math.min(first + libraryPageSize, matches.length)
  const link = number => esc(libraryLink({...filters, page: number}))
  const title = filters.topic ? libraryTopic(filters.topic).title : 'All entries'
  const description = filters.topic ? libraryTopic(filters.topic).description : ''
  const pagination = pages > 1 ? `<nav class="library-pagination" aria-label="Catalog pages">${page > 1 ? `<a class="btn secondary" href="${link(page - 1)}">Previous</a>` : ''}<span>Page ${page} of ${pages}</span>${page < pages ? `<a class="btn secondary" href="${link(page + 1)}">Next</a>` : ''}</nav>` : ''
  return `<div class="section-head library-result-head"><div><h2>${esc(title)}</h2>${description ? `<p>${esc(description)}</p>` : ''}</div><p role="status">${matches.length ? `${first + 1} to ${last} of ${matches.length}` : 'No matching entries'}</p></div>
    ${matches.length ? `<div class="hard-grid">${matches.slice(first, last).map(entry => libraryCard(entry, {...filters, page})).join('')}</div>` : '<p class="panel">Try different terms or <a href="#catalog">clear the filters</a>.</p>'}${pagination}`
}

function libraryEntry(entry, filters) {
  const back = `<a class="back" href="${esc(libraryLink(filters))}">${helmet} Back to catalog</a>`
  if (!entry) return `${back}<section class="panel"><h1>Entry unavailable</h1><p>Search the catalog for the task title.</p></section>`
  const brief = taskById(entry.hubTask)
  const collection = libraryCollection(entry.collection)
  const description = entry.summary || brief?.description
  const metric = entry.metric || brief?.metric
  const grading = entry.grading || brief?.grading || entry.grades.map(grade => gradeRoutes[grade].detail).join(' ')
  const englishSources = new Set(entry.english?.links?.map(link => link.url))
  const links = (entry.links ?? []).filter(link => !englishSources.has(link.url))
  const seen = new Set(links.map(link => link.url))
  for (const url of englishSources) seen.add(url)
  const archives = collection.links.filter(link => !seen.has(link.url))
  const linksList = items => items.length ? `<ul class="library-sources">${items.map(item => `<li><a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">${esc(item.label)}</a></li>`).join('')}</ul>` : ''
  const materials = entry.materials
  const materialDetails = materials ? `<dl class="library-materials">
    <div><dt>Statement</dt><dd>${esc(materials.statement.detail)}</dd></div>
    <div><dt>Data</dt><dd>${esc(materials.data.detail)}</dd></div>
    ${materials.submission ? `<div><dt>Submission</dt><dd>${esc(materials.submission)}</dd></div>` : ''}</dl>` : ''
  const briefLinks = brief ? `<div class="free-actions"><a class="btn" href="${esc(taskLink(brief))}">Open practice brief</a><a class="btn secondary" href="${esc(taskLink(brief, 'workspace'))}">Files and setup</a><a class="btn secondary" href="${esc(taskLink(brief, 'submissions'))}">Grading and notes</a></div>` : ''
  return `${back}<div class="task-header"><div><p class="eyebrow">${esc(entry.source || collection.title)}${entry.variant ? ` · ${esc(entry.variant)}` : ''}</p><h1>${esc(entry.title)}</h1>${description ? `<p>${esc(description)}</p>` : ''}</div></div>
    <div class="library-entry-layout"><section class="panel prose"><h2>Task materials</h2>${libraryEnglish(entry, brief)}${materialDetails || (entry.access || brief?.accessNote ? `<p>${esc(entry.access || brief.accessNote)}</p>` : '')}${linksList(links.length ? links : archives)}
      ${links.length && archives.length ? `<details><summary>Collection sources</summary>${linksList(archives)}</details>` : ''}</section>
    <section class="panel prose"><h2>Grading</h2>${libraryGrades(entry)}${metric ? `<p class="hard-metric">${esc(metric)}</p>` : ''}<p>${esc(grading)}</p>${briefLinks}</section></div>
    <p class="small muted library-record">${esc(libraryTopic(entry.topic).title)} · ${esc(entryKinds[entry.kind])} · ${esc(entry.id)}${entry.provisional ? ' · Provisional archive record' : ''}${entry.divisions?.length ? ` · <a href="https://icaic-official.github.io/docs/syllabus.html" target="_blank" rel="noopener noreferrer">Syllabus ${entry.divisions.length === 1 ? 'division' : 'divisions'} ${esc(entry.divisions.join(', '))}</a>` : ''}</p>`
}

function libraryView(params) {
  if (library.failed) return '<section class="panel"><h1>Catalog</h1><p>The catalog could not load.</p><button class="btn" id="retry-library">Try again</button></section>'
  if (!library.index) {
    loadLibrary()
    return '<div class="task-header"><div><h1>Catalog</h1><p role="status">Loading practice entries...</p></div></div>'
  }
  const filters = libraryFilters(params)
  if (params.has('entry')) return libraryEntry(library.entries.find(entry => entry.id === params.get('entry')), filters)
  const option = (id, title, chosen) => `<option value="${esc(id)}"${id === chosen ? ' selected' : ''}>${esc(title)}</option>`
  return `<div class="task-header"><div><h1>Catalog</h1><p>Find a practice task by topic, contest, or grading route.</p></div></div>
    <form id="library-filters" class="library-filters" role="search">
      <label for="library-query">Find an entry<input id="library-query" name="q" type="search" value="${esc(filters.q)}" maxlength="100" placeholder="Title, contest, or archive ID"></label>
      <label for="library-topic">Topic<select id="library-topic" name="topic"><option value="">All topics</option>${library.index.topics.map(topic => option(topic.id, topic.title, filters.topic)).join('')}</select></label>
      <label for="library-grade">Grading<select id="library-grade" name="grade"><option value="">All grading routes</option>${Object.entries(gradeRoutes).map(([id, grade]) => option(id, grade.title, filters.grade)).join('')}</select></label>
      <label for="library-english">English materials<select id="library-english" name="english"><option value="">All entries</option>${Object.entries(englishMaterials).map(([id, title]) => option(id, title, filters.english)).join('')}</select></label>
    </form><section id="library-results" aria-label="Catalog results">${libraryResults(filters)}</section>`
}

function bindLibrary() {
  const form = $('#library-filters')
  const update = () => {
    const filters = libraryFilters(new URLSearchParams(new FormData(form)))
    $('#library-results').innerHTML = libraryResults(filters)
    history.replaceState(null, '', libraryLink(filters))
  }
  form?.addEventListener('input', update)
  form?.addEventListener('submit', event => {
    event.preventDefault()
    update()
  })
  $('#retry-library')?.addEventListener('click', () => {
    library.failed = false
    render()
  })
}
