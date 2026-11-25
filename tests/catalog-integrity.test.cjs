const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const test = require('node:test')

const docs = path.join(__dirname, '..', 'docs')
const read = file => JSON.parse(fs.readFileSync(path.join(docs, file), 'utf8'))
const grades = new Set(['local', 'validation', 'samples', 'manual', 'judge', 'unknown', 'pending', 'reference'])
const statementStatuses = new Set(['found', 'partial', 'gated', 'missing'])
const dataStatuses = new Set(['public', 'self-contained', 'listed', 'partial', 'gated', 'missing', 'unknown'])

test('Catalog entries are unique and have a grading route and source', () => {
  const {topics, collections} = read('catalog/index.json')
  const topicIds = new Set()
  const entries = new Map()
  const briefs = new Set(['tasks', 'hard', 'practice'].flatMap(file => read(`${file}.json`).tasks.map(task => task.id)))
  for (const topic of topics) {
    assert.match(topic.id, /^[a-z0-9-]+$/)
    assert.ok(!topicIds.has(topic.id), topic.id)
    topicIds.add(topic.id)
    const group = read(`catalog/${topic.id}.json`)
    assert.ok(group.length > 0, topic.title)
    for (const entry of group) {
      assert.ok(entry.id && !entries.has(entry.id), entry.id)
      assert.ok(entry.title, entry.id)
      const collection = collections[entry.collection]
      assert.ok(collection?.title, entry.id)
      assert.ok(entry.grades.length && entry.grades.every(grade => grades.has(grade)), entry.id)
      const links = [...(entry.links ?? []), ...collection.links]
      assert.ok(links.length > 0, entry.id)
      for (const link of links) assert.match(link.url, /^https?:\/\//, entry.id)
      if (entry.materials) {
        const {statement, data, submission} = entry.materials
        assert.ok(statementStatuses.has(statement?.status) && statement.detail.trim(), entry.id)
        assert.ok(dataStatuses.has(data?.status) && data.detail.trim(), entry.id)
        assert.ok(submission === undefined || submission.trim(), entry.id)
        assert.ok(entry.links?.length && entry.grading?.trim(), entry.id)
      }
      if (entry.hubTask) assert.ok(briefs.has(entry.hubTask), entry.id)
      entries.set(entry.id, entry)
    }
  }

  if (topicIds.has('papers-resources')) {
    assert.equal(topics.length, 13)
    assert.equal(topics[0].title, '101')
    for (let number = 1; number <= 571; number++) {
      const id = `P${String(number).padStart(4, '0')}`
      assert.ok(entries.has(id), id)
    }
    assert.equal(entries.size, 613)
    assert.ok([...entries.values()].filter(entry => entry.materials).length >= 206)
    const mappedBriefs = new Set([...entries.values()].map(entry => entry.hubTask).filter(Boolean))
    assert.deepEqual(mappedBriefs, briefs)
  }
})
