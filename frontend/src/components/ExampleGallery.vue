<script setup>
import { signatureExamples, signatureStyles } from '../styles.js'
defineEmits(['choose'])
const styleName = id => signatureStyles.find(s => s.id === id).name
</script>

<template>
  <div class="example-gallery" aria-label="真实签名案例">
    <button v-for="example in signatureExamples" :key="example.image" type="button" class="example-card" :aria-label="`使用${example.name}的${styleName(example.style)}案例`" @click="$emit('choose', example)">
      <img :src="example.image" :alt="`${example.name} · ${styleName(example.style)}原创设计案例`">
      <div><span>{{ example.name }}</span><small>{{ styleName(example.style) }}</small></div>
    </button>
  </div>
  <p class="example-caption">真实生成的原创设计案例 · 点击填入要求，可修改姓名</p>
</template>
