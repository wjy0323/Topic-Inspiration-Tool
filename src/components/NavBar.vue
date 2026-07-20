<template>
  <nav class="navbar">
    <h1 class="navbar-title">秋芝选题站</h1>
    <div class="navbar-tabs">
      <button
        :class="{ active: currentView === 'home' }"
        @click="$emit('update:currentView', 'home')"
      >📊 榜单</button>
      <button
        :class="{ active: currentView === 'workspace' }"
        @click="$emit('update:currentView', 'workspace')"
      >💼 工作台</button>
    </div>
  </nav>
</template>

<script setup>
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
}
.navbar-tabs button.active {
  background: #1a1a2e;
  color: #fff;
  border-color: #1a1a2e;
}
</style>
