<template>
  <div class="home-page">
    <div class="home-header">
      <DatePicker v-model="selectedDate" :availableDates="availableDates" />
      <span class="home-count" v-if="!loading && products.length">{{ products.length }} 个产品</span>
      <span class="home-updated" v-if="date">更新于 {{ date }}</span>
    </div>

    <div v-if="loading" class="home-status">⏳ 加载中...</div>
    <div v-else-if="error" class="home-status home-error">{{ error }}</div>
    <div v-else-if="!products.length" class="home-status">该日期暂无数据</div>

    <div v-else class="product-list">
      <ProductCard
        v-for="(p, i) in products"
        :key="p.id"
        :product="p"
        :rank="i + 1"
        :bookmarked="isBookmarked(p.id)"
        @click="openDetail(p)"
        @toggle-bookmark="onToggleBookmark(p)"
      />
    </div>

    <ProductDetail
      :product="selectedProduct"
      :bookmarked="selectedProduct ? isBookmarked(selectedProduct.id) : false"
      :hasPrev="detailHasPrev"
      :hasNext="detailHasNext"
      :currentDate="date"
      @close="closeDetail"
      @prev="navDetail(-1)"
      @next="navDetail(1)"
      @toggle-bookmark="selectedProduct && onToggleBookmark(selectedProduct)"
    />

    <div class="home-footer" v-if="date">
      数据更新时间：{{ date }}
      <span v-if="generationError" class="home-error-tip">⚠️ 本次生成过程存在部分错误</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useData } from '../composables/useData.js'
import { useBookmarks } from '../composables/useBookmarks.js'
import DatePicker from './DatePicker.vue'
import ProductCard from './ProductCard.vue'
import ProductDetail from './ProductDetail.vue'

const { products, date, loading, error, generationError, loadDate, listAvailableDates } = useData()
const { isBookmarked, toggleBookmark } = useBookmarks()

const selectedDate = ref(getInitialDate())
const selectedProduct = ref(null)
const availableDates = ref([])

function getInitialDate() {
  const params = new URLSearchParams(window.location.search)
  if (params.get('date')) return params.get('date')
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().slice(0, 10)
}

function updateURL() {
  const params = new URLSearchParams()
  if (selectedDate.value) params.set('date', selectedDate.value)
  const qs = params.toString()
  history.replaceState(null, '', qs ? `?${qs}` : window.location.pathname)
}

function openDetail(product) {
  selectedProduct.value = product
  const params = new URLSearchParams(window.location.search)
  params.set('id', product.id)
  history.replaceState(null, '', `?${params.toString()}`)
}

function closeDetail() {
  selectedProduct.value = null
  updateURL()
}

const detailIndex = computed(() => {
  if (!selectedProduct.value) return -1
  return products.value.findIndex(p => p.id === selectedProduct.value.id)
})

const detailHasPrev = computed(() => detailIndex.value > 0)
const detailHasNext = computed(() => detailIndex.value < products.value.length - 1)

function navDetail(dir) {
  const idx = detailIndex.value + dir
  if (idx >= 0 && idx < products.value.length) {
    openDetail(products.value[idx])
  }
}

function onToggleBookmark(product) {
  toggleBookmark(product.id, {
    name_zh: product.name_zh || '',
    name: product.name || '',
    date: date.value
  })
}

function onKeydown(e) {
  if (e.key === 'Escape' && selectedProduct.value) {
    closeDetail()
  }
}

watch(selectedDate, (val) => {
  if (val) {
    loadDate(val)
    updateURL()
    closeDetail()
  }
}, { immediate: true })

// Check URL for initial detail open after products load
watch(products, (prods) => {
  const params = new URLSearchParams(window.location.search)
  const openId = params.get('id')
  if (openId) {
    const p = prods.find(p => p.id === openId)
    if (p) selectedProduct.value = p
  }
})

onMounted(async () => {
  availableDates.value = await listAvailableDates()
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.home-page { max-width: 960px; margin: 0 auto; padding: 20px 16px; }
.home-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.home-count { font-size: 14px; color: #888; }
.home-updated { font-size: 12px; color: #bbb; margin-left: auto; }
.home-status { text-align: center; padding: 60px 0; color: #999; font-size: 15px; }
.home-error { color: #c62828; }
.product-list { display: flex; flex-direction: column; gap: 16px; }
.home-footer {
  text-align: center;
  padding: 32px 0 16px;
  font-size: 12px;
  color: #ccc;
}
.home-error-tip { color: #e65100; margin-left: 8px; }
</style>
