export const signatureStyles = [
  { id: 'elegant', name: '简洁易读', description: '少装饰、清晰舒展，适合日常签写', keywords: '简洁 日常 清晰 elegant simple', instruction: '简洁易读，少装饰、清晰舒展，只生成这一款' },
  { id: 'flourish', name: '回环花式', description: '大回环、流畅连笔，收笔细长', keywords: '回环 花式 优雅 flourish loop', instruction: '回环花式，大回环、流畅连笔、细长收笔，只生成这一款' },
  { id: 'sharp', name: '利落速签', description: '紧凑前倾、转折明确，直线收笔', keywords: '利落 速签 紧凑 sharp fast', instruction: '利落速签，紧凑前倾、明确转折、直线收笔，只生成这一款' },
  { id: 'pet', name: '萌宠线描', description: '猫狗兔等小动物融入姓名笔画', keywords: '萌宠 动物 猫 狗 兔 羊 仓鼠 宠物 可爱 pet cat dog bunny cute', instruction: '萌宠线描，圆润黑色线条，把用户指定的小动物耳朵、头部或尾巴融入姓名首末笔；未指定时用原创小猫，保持姓名可读，只生成这一款' },
  { id: 'botanical', name: '花植点缀', description: '玫瑰、叶片或蝴蝶与连笔相接', keywords: '花植 花朵 玫瑰 花草 蝴蝶 植物 floral flower butterfly rose', instruction: '花植点缀，细黑线描玫瑰、叶片或蝴蝶与姓名笔画共享线条，轻盈留白，不做独立贴纸拼贴，只生成这一款' },
  { id: 'celestial', name: '星月童话', description: '月亮、星星与茶杯勾勒小故事', keywords: '星月 星星 月亮 贝壳 茶杯 魔法 童话 star moon celestial cup', instruction: '星月童话，以用户指定的月亮、星星、贝壳或茶杯为主题，将一个主图案融入姓名连笔，少量小星点缀，黑色圆润线描，只生成这一款' },
  { id: 'pastel', name: '淡彩萌系', description: '黑色轮廓配少量粉色、奶黄填色', keywords: '淡彩 萌系 彩色 粉色 奶黄 浅棕 可爱 pastel color cute', instruction: '淡彩萌系，原创可爱小动物或花植融入姓名，黑色圆润轮廓，图案内部少量淡粉、桃色、奶黄或浅棕填色；外围完全透明，保留颜色，只生成这一款' },
  { id: 'compare', name: '三款对照', description: '同一姓名对比简洁、花式与速签', keywords: '三款 对照 比较 compare all', instruction: '同一姓名分别生成简洁易读、回环花式、利落速签三款对照' },
]

export const signatureExamples = [
  { name: 'Lavine', style: 'pet', image: '/examples/lavine-pet.png', language: '英文', motif: '小猫，耳朵和尾巴与姓名笔画相连' },
  { name: 'Lavine', style: 'botanical', image: '/examples/lavine-botanical.png', language: '英文', motif: '玫瑰和蝴蝶，与姓名首末笔相连' },
  { name: 'Lavine', style: 'celestial', image: '/examples/lavine-celestial.png', language: '英文', motif: '月亮与茶杯，少量星星点缀' },
  { name: 'Lavine', style: 'pastel', image: '/examples/lavine-pastel.png', language: '英文', motif: '淡粉色兔子和奶黄色星星，与姓名笔画相连' },
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
