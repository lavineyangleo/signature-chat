<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { request } from './api.js'

const input = ref('')
const turns = ref([])
const sending = ref(false)
const hint = ref('Enter 发送 · Shift + Enter 换行')
const sample = ref(false)
const composer = ref(null)
const session = ref(localStorage.getItem('signature-chat-session') || crypto.randomUUID())
const pending = ref(null)
let timer
let alive = true
localStorage.setItem('signature-chat-session', session.value)
try { pending.value = JSON.parse(localStorage.getItem('signature-chat-pending') || 'null') } catch { /* Ignore an invalid local draft. */ }
const busy = computed(() => sending.value || turns.value.some(t => t.status === 'running'))
const hasMessages = computed(() => turns.value.length || sample.value)

async function update() {
  clearTimeout(timer)
  try {
    const snapshot = session.value
    const data = await request('/api/turns?session=' + encodeURIComponent(snapshot))
    if (!alive || session.value !== snapshot) return
    turns.value = data
    if (pending.value && data.some(t => t.id === pending.value.id)) {
      pending.value = null
      localStorage.removeItem('signature-chat-pending')
    }
    if (data.some(t => t.status === 'running')) {
      hint.value = '正在设计签名并处理透明背景…'
      timer = setTimeout(update, 2500)
    } else if (!sending.value) hint.value = 'Enter 发送 · Shift + Enter 换行'
  } catch {
    if (!alive) return
    hint.value = '连接暂时中断，正在查询已有结果；不会重发生成请求。'
    timer = setTimeout(update, 4000)
  }
}

async function bottom() {
  await nextTick()
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

async function send() {
  const text = input.value.trim()
  if (!text || busy.value) return
  if (text === '/new') {
    session.value = crypto.randomUUID()
    localStorage.setItem('signature-chat-session', session.value)
    pending.value = null
    localStorage.removeItem('signature-chat-pending')
    clearTimeout(timer)
    turns.value = []
    sample.value = false
    input.value = ''
    hint.value = '已开始新对话'
    return
  }
  if (text === '/example') {
    sample.value = true
    input.value = ''
    hint.value = '展示仓库内的真实生成样例，本次没有调用生图接口。'
    await bottom()
    return
  }
  sending.value = true
  hint.value = '正在提交…'
  // Reuse an unresolved request ID when the user deliberately resubmits the same text.
  const body = pending.value?.session === session.value && pending.value?.message === text
    ? pending.value : { id: crypto.randomUUID(), session: session.value, message: text }
  pending.value = body
  localStorage.setItem('signature-chat-pending', JSON.stringify(body))
  try {
    await request('/api/turns', body)
    input.value = ''
    await update()
    await bottom()
  } catch (error) {
    await update()
    hint.value = error.message + '；未自动重试。'
  } finally {
    sending.value = false
  }
}

function keydown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    send()
  }
}

onMounted(async () => {
  await update()
  composer.value?.focus()
})
onBeforeUnmount(() => { alive = false; clearTimeout(timer) })
</script>

<template>
  <main class="studio">
    <header><img src="/logo.svg" alt="Signature Chat" width="36" height="36"><strong>Signature Chat</strong><span>签下你的风格</span></header>
    <section class="conversation" aria-label="签名对话">
      <div v-if="!hasMessages" class="welcome"><p class="eyebrow">YOUR NAME, YOUR STYLE</p><h1>你想怎么签？</h1><p>告诉我姓名与风格，让每一次落笔都有自己的样子。</p><small>细线连笔 · 中英签名 · 透明 PNG</small></div>
      <article v-if="sample" class="sample">
        <div class="user">查看签名风格示例</div>
        <div class="assistant"><p>真实生成样例 · 简洁易读 / 回环花式 / 利落速签</p><div class="checker"><img src="/showcase-transparent.png" alt="六个姓名的三种风格透明签名对照图"></div><a href="/showcase-transparent.png" download="signature-showcase-transparent.png">下载透明 PNG ↓</a><small>本地示例，非本次实时生成。棋盘格只用于预览，不会导出。</small></div>
      </article>
      <article v-for="turn in turns" :key="turn.id">
        <div class="user">{{ turn.message }}</div>
        <div v-if="turn.status === 'running'" class="assistant pending"><span class="pulse"></span> 正在设计，完成后会显示透明签名…</div>
        <div v-else-if="turn.status === 'success'" class="assistant">
          <div class="checker"><img :src="'/images/' + turn.id + '.png'" alt="生成的透明签名"></div>
          <a :href="'/images/' + turn.id + '.png?download=1'" :download="'signature-' + turn.id.slice(0, 8) + '.png'">下载透明 PNG ↓</a>
          <small>{{ turn.metadata.width }} × {{ turn.metadata.height }} · RGBA · 棋盘格不会导出</small>
        </div>
        <div v-else class="assistant error">{{ turn.error || '生成未完成，没有自动重试。' }}</div>
      </article>
    </section>
    <footer><form @submit.prevent="send"><textarea ref="composer" v-model="input" @keydown="keydown" rows="2" maxlength="2000" aria-label="签名要求" placeholder="例如：给 Lavine 设计细线、大回环的英文签名"></textarea><button :disabled="busy" aria-label="发送签名要求" title="发送">↑</button></form><div role="status" class="hint">{{ hint }}</div><div class="commands">/example 查看示例 · /new 新对话</div></footer>
  </main>
</template>
