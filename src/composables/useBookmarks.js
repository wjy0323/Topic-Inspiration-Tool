import { ref, computed } from 'vue'
import { loadFromStorage, saveToStorage } from '../utils/storage.js'

const STORAGE_KEY = 'qiuzhi_bookmarks'
// Stored as { [id]: { id, name_zh, name, date } }
const bookmarks = ref(loadFromStorage(STORAGE_KEY, {}))

export function useBookmarks() {
  function persist() {
    saveToStorage(STORAGE_KEY, { ...bookmarks.value })
  }

  function isBookmarked(productId) {
    return productId in bookmarks.value
  }

  /**
   * Toggle bookmark. Pass productMeta (name_zh, name, date) when adding;
   * meta is stored so Workspace can display names without loading data.
   */
  function toggleBookmark(productId, productMeta = {}) {
    const next = { ...bookmarks.value }
    if (productId in next) {
      delete next[productId]
    } else {
      next[productId] = { id: productId, ...productMeta }
    }
    bookmarks.value = next
    persist()
  }

  const bookmarkList = computed(() => Object.values(bookmarks.value))

  return { bookmarks, isBookmarked, toggleBookmark, bookmarkList }
}
