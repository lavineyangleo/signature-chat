<script setup>
import { signatureExamples, signatureStyles } from '../styles.js'
defineEmits(['choose'])
const styleName = id => signatureStyles.find(s => s.id === id).name
const groups = [
  { title: '图案签名', illustrated: true, examples: signatureExamples.filter(e => e.motif) },
  { title: '连笔签名', illustrated: false, examples: signatureExamples.filter(e => !e.motif) },
]
</script>

<template>
  <section v-for="group in groups" :key="group.title" class="example-section" :aria-label="group.title">
    <p class="gallery-label">{{ group.title }}</p>
    <div class="example-gallery" :class="{ illustrated: group.illustrated }">
    <button v-for="example in group.examples" :key="example.image" type="button" class="example-card" :aria-label="`使用${example.name}的${styleName(example.style)}案例`" @click="$emit('choose', example)">
      <img :src="example.image" :alt="`${example.name} · ${styleName(example.style)}原创设计案例`">
      <div><span>{{ example.name }}</span><small>{{ styleName(example.style) }}</small></div>
    </button>
    </div>
  </section>
  <p class="example-caption">真实生成的原创设计案例 · 点击选择模式，再填写姓名</p>
</template>
