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
    toggleBookmark('prod-1', { name_zh: '测试产品', name: 'Test Product', date: '2026-07-19' })
    expect(isBookmarked('prod-1')).toBe(true)
    expect(bookmarkList.value.length).toBe(1)
    expect(bookmarkList.value[0].name_zh).toBe('测试产品')
    toggleBookmark('prod-1')
    expect(isBookmarked('prod-1')).toBe(false)
  })
})
