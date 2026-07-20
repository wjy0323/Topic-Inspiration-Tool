import { ref } from 'vue'

const BASE = '/data/'

export function useData() {
  const products = ref([])
  const date = ref('')
  const loading = ref(false)
  const error = ref('')
  const generationError = ref(false)

  async function loadDate(dateStr) {
    loading.value = true
    error.value = ''
    generationError.value = false

    try {
      const url = `${BASE}${dateStr}.json`
      const resp = await fetch(url)
      if (!resp.ok) {
        if (resp.status === 404) {
          error.value = '该日期暂无数据'
        } else {
          error.value = `加载失败 (${resp.status})`
        }
        products.value = []
        date.value = dateStr
        return
      }
      const data = await resp.json()
      products.value = data.products || []
      date.value = dateStr
      generationError.value = data.generation_error || false
    } catch (e) {
      error.value = '网络加载失败，请检查网络后重试'
      products.value = []
      date.value = dateStr
    } finally {
      loading.value = false
    }
  }

  async function listAvailableDates() {
    // CloudBase static hosting doesn't support directory listing.
    // We ship a dates.json manifest updated by CI. Fallback: empty.
    try {
      const resp = await fetch(`${BASE}dates.json`)
      if (resp.ok) {
        const data = await resp.json()
        return data.dates || []
      }
    } catch {}
    return []
  }

  return { products, date, loading, error, generationError, loadDate, listAvailableDates }
}
