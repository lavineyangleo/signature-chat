<script setup>
defineProps({ options: Array, active: Number })
defineEmits(['choose', 'activate'])
</script>

<template>
  <div class="style-menu" @mousedown.prevent>
    <div class="style-menu-heading">选择签名风格 <span>↑↓ 选择 · Enter 确定 · Esc 关闭</span></div>
    <div id="signature-style-options" role="listbox" aria-label="签名风格">
      <button v-for="(style, index) in options" :id="'style-option-' + style.id" :key="style.id" type="button" role="option" :aria-selected="index === active" :class="{ active: index === active }" @mouseenter="$emit('activate', index)" @click="$emit('choose', style)">
        <strong>{{ style.name }}</strong><span>{{ style.description }}</span><i v-if="index === active" aria-hidden="true">↵</i>
      </button>
      <p v-if="!options.length" class="no-style">没有匹配风格，试试“花式”或按 Esc 继续输入。</p>
    </div>
  </div>
</template>
