<template>
  <div class="product-analysis">
    <p class="analysis-note">内容来自产品介绍，未实际试用。实现思路是分析建议，不代表官方方案。</p>
    <section v-for="section in sections" :key="section.key">
      <h4>{{ section.title }}</h4>
      <dl>
        <template v-for="field in section.fields" :key="field.key">
          <dt>{{ field.label }}</dt>
          <dd>{{ product[section.key]?.[field.key] || '暂无分析' }}</dd>
        </template>
      </dl>
      <details v-if="section.key === 'technical_analysis'" class="source-details">
        <summary>介绍说了什么，还有什么没说清</summary>
        <p>{{ product.technical_analysis?.disclosed_facts || '介绍没说具体用什么技术。' }}</p>
        <p>{{ product.technical_analysis?.unknowns || '暂无补充。' }}</p>
      </details>
    </section>
    <section>
      <h4>做产品时，可以借用哪一点</h4>
      <ul v-if="product.transferable_insights?.length">
        <li v-for="(item, index) in product.transferable_insights" :key="index">{{ item }}</li>
      </ul>
      <p v-else>暂无分析</p>
    </section>
    <section>
      <h4>如果试用，先看这两件事</h4>
      <ul v-if="product.validation_questions?.length">
        <li v-for="(item, index) in product.validation_questions" :key="index">{{ item }}</li>
      </ul>
      <p v-else>暂无分析</p>
    </section>
  </div>
</template>

<script setup>
defineProps({ product: { type: Object, required: true } })

const sections = [
  { key: 'product_analysis', title: '先弄懂它做什么', fields: [
    { key: 'target_problem', label: '谁会需要它' },
    { key: 'workflow', label: '具体怎么用' },
    { key: 'ai_value', label: 'AI 在里面干了什么' },
    { key: 'differentiation', label: '比原来的做法好在哪' }
  ] },
  { key: 'technical_analysis', title: '从技术上看，怎么做出来', fields: [
    { key: 'possible_approach', label: '一种可行的做法 · 非官方方案' },
    { key: 'tradeoffs', label: '哪一步最容易出问题' }
  ] }
]
</script>

<style scoped>
.product-analysis { margin-bottom: 20px; font-size: 14px; line-height: 1.7; color: #444; }
.analysis-note { font-size: 12px; color: #666; }
section { background: #f5f7fb; border: 1px solid #e4e8f0; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
h4 { margin: 0 0 12px; font-size: 15px; color: #222; }
dl, p { margin: 0; }
dt { font-weight: 600; margin-top: 12px; }
dt:first-child { margin-top: 0; }
dd { margin: 4px 0 0; white-space: pre-line; overflow-wrap: anywhere; }
ul { padding-left: 20px; margin: 0; }
li + li { margin-top: 8px; }
.source-details { margin-top: 14px; font-size: 13px; color: #666; }
.source-details summary { cursor: pointer; }
.source-details p { margin-top: 8px; }
</style>
