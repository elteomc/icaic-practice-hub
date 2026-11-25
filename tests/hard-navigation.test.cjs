const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const test = require('node:test')
const vm = require('node:vm')

const docs = path.join(__dirname, '..', 'docs')

async function open(hash) {
  const app = {innerHTML: '', textContent: ''}
  const browser = vm.createContext({
    URLSearchParams,
    location: {hash},
    localStorage: {getItem: () => null},
    document: {querySelector: selector => {
      if (selector === '#app') return app
      if (selector === '#profile') return {addEventListener() {}}
      return null
    }},
    addEventListener() {},
    setInterval() {},
    async fetch(resource) {
      const file = path.join(docs, resource.split('?')[0])
      return {ok: fs.existsSync(file), async json() { return JSON.parse(fs.readFileSync(file, 'utf8')) }}
    }
  })
  for (const asset of ['hard.js', 'free.js']) {
    const file = path.join(docs, asset)
    if (fs.existsSync(file)) vm.runInContext(fs.readFileSync(file, 'utf8'), browser)
  }
  await new Promise(resolve => setImmediate(resolve))
  return app.innerHTML
}

test('O7 and the old Hard? bookmark open the same collection', async () => {
  const page = await open('#o7')
  assert.match(page, /<h1>O7<\/h1>/)
  assert.equal(await open('#hard'), page)
  for (const title of ['InstRead', 'PolERo', 'Uneasy Alliances', 'Industrial Quality Control', 'EEG Cross-Task Transfer', 'Global Campus']) {
    assert.ok(page.includes(title), title)
  }
})

test('ez opens a broad list and includes the earlier easy shortlist', async () => {
  const page = await open('#ez')
  assert.match(page, /<h1>ez<\/h1>/)
  assert.ok((page.match(/data-practice-task/g) || []).length >= 24)
  for (const title of ['Stats 101', 'Probability 101', 'Neural Playground', 'Radioactive Decay', 'University Admissions', 'Basketball Shooting', 'Deceptive Points', 'Face Matching', 'Sound of Nature', 'Multimodal Embeddings', 'Air Temperature Forecasting', 'Lost Interpreter']) {
    assert.ok(page.includes(title), title)
  }
})

test('realeyes offers the same task page with an optional hint and a return link', async () => {
  const list = await open('#realeyes')
  assert.match(list, /<h1>realeyes<\/h1>/)
  assert.match(list, /Dieting Network/)
  assert.match(list, /#task=radioactive-decay&amp;via=realeyes/)
  assert.doesNotMatch(list, /<details/)
  const task = await open('#task=radioactive-decay&via=realeyes')
  assert.match(task, /class="back" href="#realeyes"/)
  assert.match(task, /<details class="practice-hint">/)
  assert.match(task, /tab=workspace&amp;via=realeyes/)
})

test('An O7 task links to its own evaluator and never offers an original-task upload', async () => {
  const page = await open('#task=instread&tab=submissions')
  assert.match(page, /<h1>InstRead<\/h1>/)
  assert.match(page, /judge\.nitro-ai\.org\/competitions\/nitro\/nitro-nlp-hackathon-2026\/1\/view/)
  assert.doesNotMatch(page, /\/issues\/new/)
})

test('A direct link to an original task still opens its notebook and task pack', async () => {
  const page = await open('#task=admissions&tab=workspace')
  assert.match(page, /<h1>University Admissions<\/h1>/)
  assert.match(page, /packs\/admissions\.zip/)
  assert.match(page, /Open in Colab/)
})

test('The original task statement and grading tab explain the available route', async () => {
  const overview = await open('#task=admissions')
  assert.match(overview, /Grading &amp; notes/)
  assert.doesNotMatch(overview, /through the hub|cloud submission/)
  const grading = await open('#task=admissions&tab=submissions')
  assert.match(grading, /cloud_grade\.py --local admissions/)
  assert.match(grading, /#grade-an-original-task-locally/)
  assert.doesNotMatch(grading, /\/issues\/new/)
})
