import { ref, computed } from 'vue'
import { loadFromStorage, saveToStorage } from '../utils/storage.js'

const STORAGE_KEY = 'qiuzhi_bookmarks'
const bookmarks = ref(new Set(loadFromStorage(STORAGE_KEY, [])))

export function useBookmarks() {
  function persist() {
    saveToStorage(STORAGE_KEY, [...bookmarks.value])
  }

  function isBookmarked(productId) {
    return bookmarks.value.has(productId)
  }

  function toggleBookmark(productId) {
    const s = new Set(bookmarks.value)
    if (s.has(productId)) {
      s.delete(productId)
    } else {
      s.add(productId)
    }
    bookmarks.value = s
    persist()
  }

  const bookmarkList = computed(() => [...bookmarks.value])

  return { bookmarks, isBookmarked, toggleBookmark, bookmarkList }
}
