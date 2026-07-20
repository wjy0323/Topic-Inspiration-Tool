import { describe, it, expect, beforeEach } from 'vitest'
import { useBookmarks } from '../useBookmarks.js'

describe('useBookmarks', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with empty bookmarks', () => {
    const { bookmarkList } = useBookmarks()
    expect(bookmarkList.value).toEqual([])
  })

  it('toggleBookmark adds and removes', () => {
    const { isBookmarked, toggleBookmark, bookmarkList } = useBookmarks()
    expect(isBookmarked('prod-1')).toBe(false)
    toggleBookmark('prod-1')
    expect(isBookmarked('prod-1')).toBe(true)
    expect(bookmarkList.value).toContain('prod-1')
    toggleBookmark('prod-1')
    expect(isBookmarked('prod-1')).toBe(false)
  })
})
