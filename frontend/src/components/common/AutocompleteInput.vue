<template>
  <div class="autocomplete-wrapper">
    <input
      ref="inputRef"
      v-model="inputValue"
      @input="handleInput"
      @focus="showSuggestions = true"
      @blur="handleBlur"
      @keydown.down.prevent="highlightNext"
      @keydown.up.prevent="highlightPrevious"
      @keydown.enter.prevent="selectHighlighted"
      @keydown.esc="closeSuggestions"
      class="form-input"
      type="text"
      :placeholder="placeholder"
      :required="required"
    />
    <div v-if="showSuggestions && filteredSuggestions.length > 0" class="autocomplete-dropdown">
      <div
        v-for="(item, index) in filteredSuggestions"
        :key="item.id"
        :class="['autocomplete-item', { highlighted: index === highlightedIndex }]"
        @mousedown.prevent="selectItem(item)"
        @mouseenter="highlightedIndex = index"
      >
        {{ displayField ? item[displayField] : item.name }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import api from '../../utils/api'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  endpoint: {
    type: String,
    required: true,
  },
  displayField: {
    type: String,
    default: 'name',
  },
  valueField: {
    type: String,
    default: 'id',
  },
  placeholder: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'select'])

const inputValue = ref('')
const suggestions = ref([])
const showSuggestions = ref(false)
const highlightedIndex = ref(-1)
const inputRef = ref(null)
const selectedItem = ref(null)

// 入力値が変更されたときに候補を取得
const handleInput = async () => {
  // 入力が変更された場合、選択状態を解除（ただし、空の場合は下で処理）
  if (selectedItem.value && inputValue.value !== selectedItem.value[props.displayField]) {
    selectedItem.value = null
    emit('select', null)
  }

  if (inputValue.value.length === 0) {
    emit('update:modelValue', null)
    emit('select', null)
    selectedItem.value = null
  }

  try {
    const response = await api.get(props.endpoint, {
      params: { search: inputValue.value },
    })
    suggestions.value = response.data
    showSuggestions.value = true
    highlightedIndex.value = -1

    // 候補が1つに絞られたら自動選択
    if (suggestions.value.length === 1) {
      selectItem(suggestions.value[0])
    }
  } catch (error) {
    console.error('Failed to fetch suggestions:', error)
    suggestions.value = []
  }
}

const filteredSuggestions = computed(() => {
  return suggestions.value
})

const selectItem = (item) => {
  inputValue.value = item[props.displayField]
  selectedItem.value = item
  emit('update:modelValue', item[props.valueField])
  emit('select', item)
  showSuggestions.value = false
}

const handleBlur = () => {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

const closeSuggestions = () => {
  showSuggestions.value = false
}

const highlightNext = () => {
  if (highlightedIndex.value < filteredSuggestions.value.length - 1) {
    highlightedIndex.value++
  }
}

const highlightPrevious = () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
  }
}

const selectHighlighted = () => {
  if (highlightedIndex.value >= 0 && highlightedIndex.value < filteredSuggestions.value.length) {
    selectItem(filteredSuggestions.value[highlightedIndex.value])
  }
}

// 外部からの値変更に対応
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && (!selectedItem.value || selectedItem.value[props.valueField] !== newVal)) {
      // IDから名前を取得（idパラメータを渡して特定のアイテムを取得）
      api.get(props.endpoint, { params: { id: newVal } }).then((response) => {
        const item = response.data.find((i) => i[props.valueField] === newVal)
        if (item) {
          inputValue.value = item[props.displayField]
          selectedItem.value = item
        }
      })
    } else if (!newVal) {
      inputValue.value = ''
      selectedItem.value = null
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.autocomplete-wrapper {
  position: relative;
  width: 100%;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid var(--border);
  border-top: none;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.autocomplete-item {
  padding: 10px;
  cursor: pointer;
  transition: background-color 0.15s;
  border-bottom: 1px solid #f0f0f0;
}

.autocomplete-item:hover,
.autocomplete-item.highlighted {
  background-color: var(--light-bg);
}

.autocomplete-item:last-child {
  border-bottom: none;
}
</style>
