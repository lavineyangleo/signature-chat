export const signatureStyles = [
  { id: 'elegant', name: '简洁易读', description: '少装饰、清晰舒展，适合日常签写', keywords: '简洁 日常 清晰 elegant simple', instruction: '简洁易读，少装饰、清晰舒展，只生成这一款' },
  { id: 'flourish', name: '回环花式', description: '大回环、流畅连笔，收笔细长', keywords: '回环 花式 优雅 flourish loop', instruction: '回环花式，大回环、流畅连笔、细长收笔，只生成这一款' },
  { id: 'sharp', name: '利落速签', description: '紧凑前倾、转折明确，直线收笔', keywords: '利落 速签 紧凑 sharp fast', instruction: '利落速签，紧凑前倾、明确转折、直线收笔，只生成这一款' },
  { id: 'compare', name: '三款对照', description: '同一姓名对比简洁、花式与速签', keywords: '三款 对照 比较 compare all', instruction: '同一姓名分别生成简洁易读、回环花式、利落速签三款对照' },
]

export const signatureExamples = [
  { name: 'Lavine', style: 'elegant', image: '/examples/lavine-elegant.png', language: '英文' },
  { name: 'Robert', style: 'flourish', image: '/examples/robert-flourish.png', language: '英文' },
  { name: 'Alice', style: 'sharp', image: '/examples/alice-sharp.png', language: '英文' },
  { name: '周润发', style: 'elegant', image: '/examples/zhou-elegant.png', language: '中文' },
  { name: '刘德华', style: 'flourish', image: '/examples/liu-flourish.png', language: '中文' },
  { name: '赵丽颖', style: 'sharp', image: '/examples/zhao-sharp.png', language: '中文' },
]

export function styleText(style) {
  return `【风格：${style.instruction}】`
}
