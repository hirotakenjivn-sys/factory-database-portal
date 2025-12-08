<template>
  <div v-if="show" class="error-dialog-overlay" @click="handleOverlayClick">
    <div class="error-dialog" @click.stop>
      <div class="error-dialog-header">
        <h3>{{ title || 'エラー' }}</h3>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="error-dialog-body">
        <div class="error-message" ref="messageRef">{{ message }}</div>
      </div>
      <div class="error-dialog-footer">
        <button class="btn btn-secondary" @click="copyToClipboard">コピー</button>
        <button class="btn btn-primary" @click="close">閉じる</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'エラー'
  },
  message: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

const messageRef = ref(null)

const close = () => {
  emit('close')
}

const handleOverlayClick = () => {
  close()
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.message)
    alert('コピーしました')
  } catch (error) {
    // フォールバック: テキスト選択
    if (messageRef.value) {
      const range = document.createRange()
      range.selectNodeContents(messageRef.value)
      const selection = window.getSelection()
      selection.removeAllRanges()
      selection.addRange(range)
      try {
        document.execCommand('copy')
        alert('コピーしました')
      } catch (err) {
        alert('コピーに失敗しました。手動で選択してコピーしてください。')
      }
    }
  }
}
</script>

<style scoped>
.error-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.error-dialog {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.error-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.error-dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #dc2626;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.error-dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.error-message {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #1f2937;
  white-space: pre-wrap;
  word-break: break-word;
  background-color: #f9fafb;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  user-select: text;
  cursor: text;
}

.error-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background-color: #4b5563;
}
</style>
