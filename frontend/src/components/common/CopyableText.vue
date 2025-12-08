<template>
  <span
    class="copyable-text"
    :class="{ 'copied': copied }"
    @click="copyToClipboard"
    :title="copied ? 'コピーしました!' : 'クリックしてコピー'"
  >
    <slot>{{ text }}</slot>
  </span>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: ''
  }
})

const copied = ref(false)
let resetTimeout = null

const copyToClipboard = async () => {
  // スロットが使用されている場合はイベント要素のテキストを取得
  const textToCopy = props.text || event.currentTarget.textContent.trim()

  try {
    await navigator.clipboard.writeText(textToCopy)
    copied.value = true

    // 2秒後にコピー状態をリセット
    if (resetTimeout) {
      clearTimeout(resetTimeout)
    }
    resetTimeout = setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy text:', err)
    // フォールバック: 古いブラウザ対応
    const textArea = document.createElement('textarea')
    textArea.value = textToCopy
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
    } catch (err) {
      console.error('Fallback copy failed:', err)
    }
    document.body.removeChild(textArea)
  }
}
</script>

<style scoped>
.copyable-text {
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  transition: background 0.2s ease;
  user-select: none;
}

.copyable-text:hover,
.copyable-text.copied {
  background: rgba(0, 120, 212, 0.08);
  text-decoration: underline;
}

.copyable-text:active {
  transform: scale(0.98);
}
</style>
