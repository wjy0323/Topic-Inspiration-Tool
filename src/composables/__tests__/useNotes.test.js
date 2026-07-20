import { describe, it, expect, beforeEach } from 'vitest'
import { useNotes } from '../useNotes.js'

describe('useNotes', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with empty notes', () => {
    const { getNote } = useNotes()
    expect(getNote('prod-1')).toBe('')
  })

  it('saveNote persists and retrieves', () => {
    const { saveNote, getNote, notesList } = useNotes()
    saveNote('prod-1', '这是一个好选题')
    expect(getNote('prod-1')).toBe('这是一个好选题')
    expect(notesList.value.length).toBe(1)
    expect(notesList.value[0].summary).toBe('这是一个好选题')
  })

  it('saveNote with productMeta stores metadata', () => {
    const { saveNote, getNote, notesList } = useNotes()
    saveNote('prod-meta', '笔记内容', { name_zh: '测试产品', name: 'Test', date: '2026-07-19' })
    expect(getNote('prod-meta')).toBe('笔记内容')
    const entry = notesList.value.find(n => n.id === 'prod-meta')
    expect(entry).toBeTruthy()
    expect(entry.name_zh).toBe('测试产品')
    expect(entry.date).toBe('2026-07-19')
  })
})
