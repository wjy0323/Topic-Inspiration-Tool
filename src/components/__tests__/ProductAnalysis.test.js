import { describe, it, expect } from 'vitest'
import { createSSRApp, h } from 'vue'
import { renderToString } from '@vue/server-renderer'
import ProductCard from '../ProductCard.vue'
import ProductAnalysis from '../ProductAnalysis.vue'
import ScoreDetail from '../ScoreDetail.vue'

const render = (component, props) => renderToString(createSSRApp({ render: () => h(component, props) }))
const scores = {
  product_value: { score: 4, reason: '问题具体' },
  technical_insight: { score: null, reason: '信息不足，缺少技术文档' },
  transferability: { score: 3, reason: '工作流可迁移' }
}

describe('产品研究展示', () => {
  it('新卡片使用研究评分，将未知与低分区分', async () => {
    const html = await render(ProductCard, { product: { id: '1', name: 'Example', scores }, rank: 1 })
    expect(html).toContain('产品价值')
    expect(html).toContain('技术启发')
    expect(html).toContain('可借鉴性')
    expect(html).toContain('待评估')
    expect(html).not.toContain('视频化')
    const detail = await render(ScoreDetail, { scores })
    expect(detail).toContain('信息不足，缺少技术文档')
    expect(detail).toContain('待评估')
  })

  it('历史数据仍显示原有评分，避免把视频评分误标为产品价值', async () => {
    const html = await render(ProductCard, {
      product: { id: '1', name: 'Old', scores: { video_suitability: { score: 5 } } }, rank: 1
    })
    expect(html).toContain('视频化')
    expect(html).not.toContain('产品价值')
  })

  it('完整呈现拆解、证据边界和验证问题，按文本处理模型内容', async () => {
    const html = await render(ProductAnalysis, { product: {
      product_analysis: { target_problem: '用户资料归档' },
      technical_analysis: { possible_approach: '推断，待验证：自动分类' },
      transferable_insights: ['分类后由用户确认'],
      validation_questions: ['<script>alert(1)</script>']
    } })
    for (const text of ['先弄懂它做什么', '从技术上看，怎么做出来', '做产品时，可以借用哪一点', '如果试用，先看这两件事', '内容来自产品介绍，未实际试用', '分类后由用户确认']) {
      expect(html).toContain(text)
    }
    expect(html).toContain('&lt;script&gt;')
    expect(html).not.toContain('<script>')
  })
})
