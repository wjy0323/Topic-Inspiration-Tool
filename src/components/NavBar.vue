<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <img src="../icon.png" alt="logo" class="navbar-logo" />
      <h1 class="navbar-title">AI产品灵感日报</h1>
    </div>
    <div class="navbar-tabs">
      <button
        :class="{ active: currentView === 'home' }"
        @click="$emit('update:currentView', 'home')"
      ><LayoutGrid :size="16" /> 榜单</button>
      <button
        :class="{ active: currentView === 'workspace' }"
        @click="$emit('update:currentView', 'workspace')"
      ><Briefcase :size="16" /> 工作台</button>
    </div>
  </nav>
</template>

<script setup>
import { LayoutGrid, Briefcase } from '@lucide/vue'
defineProps({
  currentView: { type: String, required: true }
})
defineEmits(['update:currentView'])
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}
.navbar-logo {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  object-fit: cover;
}
.navbar-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}
.navbar-tabs {
  display: flex;
  gap: 8px;
}
.navbar-tabs button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.navbar-tabs button.active {
  background: #1a1a2e;
  color: #fff;
  border-color: #1a1a2e;
}
</style>
