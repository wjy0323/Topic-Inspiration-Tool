import { ref, computed } from 'vue'
import { loadFromStorage, saveToStorage } from '../utils/storage.js'

const STORAGE_KEY = 'qiuzhi_notes'
const notes = ref(loadFromStorage(STORAGE_KEY, {}))

export function useNotes() {
  function persist() {
    saveToStorage(STORAGE_KEY, { ...notes.value })
  }

  function getNote(productId) {
    return notes.value[productId] || ''
  }

  function saveNote(productId, text) {
    notes.value = { ...notes.value, [productId]: text }
    persist()
  }

  const notesList = computed(() => {
    return Object.entries(notes.value)
      .filter(([, text]) => text.trim().length > 0)
      .map(([id, text]) => ({ id, text, summary: text.slice(0, 50) }))
  })

  return { notes, getNote, saveNote, notesList }
}
