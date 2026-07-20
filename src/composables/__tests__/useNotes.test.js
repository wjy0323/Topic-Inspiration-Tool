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
})
