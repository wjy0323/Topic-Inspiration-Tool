import { ref, computed } from 'vue'
import { loadFromStorage, saveToStorage } from '../utils/storage.js'

const STORAGE_KEY = 'qiuzhi_notes'
// Stored as { [id]: { text, name_zh, name, date } }
const notes = ref(loadFromStorage(STORAGE_KEY, {}))

export function useNotes() {
  function persist() {
    saveToStorage(STORAGE_KEY, { ...notes.value })
  }

  function getNote(productId) {
    const entry = notes.value[productId]
    if (!entry) return ''
    return typeof entry === 'string' ? entry : entry.text || ''
  }

  /**
   * Save a note. Pass productMeta (name_zh, name, date) so Workspace
   * can display product names without loading data.
   */
  function saveNote(productId, text, productMeta = {}) {
    const existing = notes.value[productId] || {}
    const prev = typeof existing === 'string' ? { text: existing } : existing
    notes.value = {
      ...notes.value,
      [productId]: { ...prev, ...productMeta, text }
    }
    persist()
  }

  const notesList = computed(() => {
    return Object.entries(notes.value)
      .filter(([, entry]) => {
        const t = typeof entry === 'string' ? entry : entry.text || ''
        return t.trim().length > 0
      })
      .map(([id, entry]) => {
        const text = typeof entry === 'string' ? entry : entry.text || ''
        const name_zh = typeof entry === 'object' ? entry.name_zh : undefined
        const name = typeof entry === 'object' ? entry.name : undefined
        const date = typeof entry === 'object' ? entry.date : undefined
        return { id, text, summary: text.slice(0, 50), name_zh, name, date }
      })
  })

  return { notes, getNote, saveNote, notesList }
}
