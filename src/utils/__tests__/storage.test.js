import { describe, it, expect, beforeEach } from 'vitest'
import { loadFromStorage, saveToStorage } from '../storage.js'

describe('loadFromStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns fallback when key does not exist', () => {
    expect(loadFromStorage('nonexistent', [])).toEqual([])
  })

  it('returns parsed value when key exists', () => {
    localStorage.setItem('test', JSON.stringify({ a: 1 }))
    expect(loadFromStorage('test', {})).toEqual({ a: 1 })
  })

  it('returns fallback on corrupted JSON', () => {
    localStorage.setItem('bad', '{corrupted')
    expect(loadFromStorage('bad', 'fallback')).toBe('fallback')
  })
})

describe('saveToStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('saves value as JSON string', () => {
    saveToStorage('test', { b: 2 })
    expect(localStorage.getItem('test')).toBe('{"b":2}')
  })
})
