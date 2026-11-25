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

test('Hard? opens its own list and links the requested tasks and Global Campus', async () => {
  const page = await open('#hard')
  assert.match(page, /<h1>Hard\?<\/h1>/)
  for (const title of ['InstRead', 'PolERo', 'Uneasy Alliances', 'Industrial Quality Control', 'EEG Cross-Task Transfer', 'Global Campus']) {
    assert.ok(page.includes(title), title)
  }
})

test('A Hard? task links to its own evaluator and never offers an original-task upload', async () => {
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
