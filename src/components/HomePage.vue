<template>
  <div class="home-layout">
    <!-- ── Sidebar ── -->
    <aside class="home-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h2 class="sidebar-title"><Newspaper :size="18" /> 选题灵感日报</h2>
        <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed" :title="sidebarCollapsed ? '展开' : '收起'">
          <ChevronRight v-if="sidebarCollapsed" :size="16" />
          <ChevronLeft v-else :size="16" />
        </button>
      </div>
      <nav class="sidebar-nav">
        <button
          v-for="d in availableDates"
          :key="d"
          class="sidebar-date"
          :class="{ active: d === selectedDate }"
          @click="selectDate(d)"
        >
          <Calendar :size="14" class="date-icon" />
          <span class="date-label">{{ formatDate(d) }}</span>
        </button>
        <div v-if="availableDates.length === 0" class="sidebar-empty">暂无历史日报</div>
      </nav>
    </aside>

    <!-- ── Main ── -->
    <div class="home-main">
      <div class="home-header">
        <span class="home-count" v-if="!loading && products.length">{{ products.length }} 个产品</span>
        <span class="home-updated" v-if="date">更新于 {{ date }}</span>
      </div>

      <div v-if="loading" class="home-status"><Loader2 :size="18" class="spin" /> 加载中...</div>
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
          @open-notes="openDetail(p)"
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
        <span v-if="generationError" class="home-error-tip"><AlertTriangle :size="14" /> 本次生成过程存在部分错误</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useData } from '../composables/useData.js'
import { useBookmarks } from '../composables/useBookmarks.js'
import { Newspaper, Calendar, ChevronLeft, ChevronRight, Loader2, AlertTriangle } from '@lucide/vue'
import ProductCard from './ProductCard.vue'
import ProductDetail from './ProductDetail.vue'

const { products, date, loading, error, generationError, loadDate, listAvailableDates } = useData()
const { isBookmarked, toggleBookmark } = useBookmarks()

const selectedDate = ref(getInitialDate())
const selectedProduct = ref(null)
const availableDates = ref([])
const sidebarCollapsed = ref(false)

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  if (isNaN(d.getTime())) return dateStr
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

function selectDate(d) {
  if (d !== selectedDate.value) {
    selectedDate.value = d
  }
}

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
/* ── Layout ── */
.home-layout {
  display: flex;
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
}

/* ── Sidebar ── */
.home-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #fafbfc;
  border-right: 1px solid #e5e5e5;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  transition: width 0.25s, padding 0.25s;
  overflow: hidden;
}
.home-sidebar.collapsed {
  width: 44px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 12px;
}
.home-sidebar.collapsed .sidebar-header {
  padding: 0 10px;
  justify-content: center;
}
.sidebar-title {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}
.home-sidebar.collapsed .sidebar-title {
  display: none;
}
.sidebar-toggle {
  background: none;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 12px;
  cursor: pointer;
  color: #888;
  flex-shrink: 0;
}
.sidebar-toggle:hover {
  background: #eee;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 8px;
}
.home-sidebar.collapsed .sidebar-nav {
  padding: 0 4px;
}

.date-icon { flex-shrink: 0; color: #999; }
.sidebar-date {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  text-align: left;
  transition: background 0.15s;
  white-space: nowrap;
}
.home-sidebar.collapsed .sidebar-date {
  justify-content: center;
  padding: 10px 6px;
}
.sidebar-date:hover {
  background: #eef3ff;
}
.sidebar-date.active {
  background: #e0e7ff;
  color: #3b5998;
  font-weight: 600;
}
.date-icon {
  font-size: 14px;
  flex-shrink: 0;
}
.home-sidebar.collapsed .date-label {
  display: none;
}

.sidebar-empty {
  padding: 20px 12px;
  color: #bbb;
  font-size: 13px;
  text-align: center;
}

/* ── Main ── */
.home-main {
  flex: 1;
  min-width: 0;
  padding: 20px 24px;
}

.home-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.home-count { font-size: 14px; color: #888; }
.home-updated { font-size: 12px; color: #bbb; margin-left: auto; }
.home-status { text-align: center; padding: 60px 0; color: #999; font-size: 15px; display: flex; align-items: center; justify-content: center; gap: 8px; }
.home-error { color: #c62828; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.product-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.home-footer {
  text-align: center;
  padding: 32px 0 16px;
  font-size: 12px;
  color: #ccc;
}
.home-error-tip { color: #e65100; margin-left: 8px; display: inline-flex; align-items: center; gap: 4px; }

/* ── Responsive ── */
@media (max-width: 900px) {
  .home-layout {
    flex-direction: column;
  }
  .home-sidebar {
    width: 100%;
    flex-shrink: 1;
    border-right: none;
    border-bottom: 1px solid #e5e5e5;
    padding: 12px 0;
  }
  .home-sidebar.collapsed {
    width: 100%;
  }
  .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 4px;
    overflow-y: visible;
    padding: 0 12px;
  }
  .home-sidebar.collapsed .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .sidebar-title {
    font-size: 14px;
  }
  .home-sidebar.collapsed .sidebar-title {
    display: block;
  }
  .home-sidebar.collapsed .date-label {
    display: inline;
  }
  .sidebar-toggle {
    display: none;
  }
  .sidebar-date {
    padding: 6px 10px;
    font-size: 13px;
  }
  .home-main {
    padding: 16px;
  }
}

@media (max-width: 680px) {
  .product-list { grid-template-columns: 1fr; }
}
</style>
