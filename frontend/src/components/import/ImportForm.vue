<template>
  <div class="max-w-2xl mx-auto p-6">
    <div class="bg-base2 rounded-lg shadow-lg p-8">
      <h2 class="text-3xl font-bold text-base01 mb-6">Import Recipe</h2>
      
      <!-- Mode Switcher -->
      <div class="flex gap-2 mb-6" role="tablist">
        <button
          v-for="mode in modes"
          :key="mode.value"
          @click="switchMode(mode.value)"
          :disabled="isLoading"
          role="tab"
          :aria-selected="activeMode === mode.value"
          class="flex-1 py-3 px-4 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :class="activeMode === mode.value 
            ? 'bg-blue text-base3' 
            : 'bg-base1 text-base01 hover:bg-base0'"
        >
          {{ mode.label }}
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- URL Input -->
        <div v-show="activeMode === 'url'" role="tabpanel">
          <label for="url" class="block text-sm font-medium text-base01 mb-2">
            Recipe URL
          </label>
          <input
            id="url"
            v-model="urlInput"
            type="url"
            placeholder="https://example.com/recipe"
            class="w-full px-4 py-3 bg-base3 border-2 border-base1 rounded-lg focus:outline-none focus:border-blue text-base00 placeholder-base1"
            :disabled="isLoading"
          />
        </div>
        
        <!-- Text Input -->
        <div v-show="activeMode === 'text'" role="tabpanel">
          <label for="text" class="block text-sm font-medium text-base01 mb-2">
            Recipe Text
          </label>
          <textarea
            id="text"
            v-model="textInput"
            rows="10"
            placeholder="Paste your recipe text here..."
            class="w-full px-4 py-3 bg-base3 border-2 border-base1 rounded-lg focus:outline-none focus:border-blue text-base00 placeholder-base1 resize-y"
            :disabled="isLoading"
          ></textarea>
          <div class="flex justify-between items-center mt-2">
            <p class="text-sm text-base01">
              Paste the full recipe text including ingredients and instructions
            </p>
            <p class="text-sm text-base01">
              {{ textInput.length }} / 50,000 chars
            </p>
          </div>
        </div>
        
        <!-- PDF Upload -->
        <div v-show="activeMode === 'pdf'" role="tabpanel">
          <label for="pdf" class="block text-sm font-medium text-base01 mb-2">
            Recipe PDF
          </label>
          <input
            id="pdf"
            ref="fileInput"
            type="file"
            accept=".pdf"
            @change="handleFileSelect"
            :disabled="isLoading"
            class="w-full px-4 py-3 bg-base3 border-2 border-base1 rounded-lg focus:outline-none focus:border-blue text-base00 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue file:text-base3 hover:file:bg-cyan file:cursor-pointer"
          />
          
          <!-- File Preview -->
          <div v-if="selectedFile" class="mt-4 p-4 bg-base3 rounded-lg border-2 border-base1">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-semibold text-base01">{{ selectedFile.name }}</p>
                <p class="text-sm text-base00">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
              <button
                type="button"
                @click="clearFile"
                :disabled="isLoading"
                class="px-4 py-2 bg-red text-base3 rounded-lg hover:bg-opacity-80 transition-colors disabled:opacity-50"
              >
                Remove
              </button>
            </div>
          </div>
          
          <p class="text-sm text-base01 mt-2">
            Upload a PDF file containing the recipe (max 10MB)
          </p>
        </div>
        
        <button
          type="submit"
          :disabled="isSubmitDisabled"
          class="w-full py-3 px-6 rounded-lg font-semibold text-base3 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :class="isLoading ? 'bg-base1' : 'bg-blue hover:bg-cyan'"
        >
          <span v-if="isLoading">{{ loadingMessage }}</span>
          <span v-else>Import Recipe</span>
        </button>
      </form>
      
      <!-- Success Message -->
      <div
        v-if="result"
        class="mt-6 p-4 bg-green bg-opacity-10 border-2 border-green rounded-lg"
      >
        <p class="text-green font-semibold">
          ✓ Recipe imported successfully: 
          <a :href="`/recipe/import/${result.filename}`" class="underline hover:text-cyan">
            {{ result.filename }}
          </a>
        </p>
      </div>
      
      <!-- Error Message -->
      <div
        v-if="error"
        class="mt-6 p-4 bg-red bg-opacity-10 border-2 border-red rounded-lg"
      >
        <p class="text-red font-semibold">✗ {{ error }}</p>
      </div>
      
      <!-- Loading Indicator -->
      <div v-if="isLoading" class="mt-6 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-base1 border-t-blue"></div>
        <p class="mt-2 text-base01">{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useImport } from '../../composables/useImport'

const modes = [
  { value: 'url', label: 'URL' },
  { value: 'text', label: 'Text' },
  { value: 'pdf', label: 'PDF' }
]

const activeMode = ref('url')
const urlInput = ref('')
const textInput = ref('')
const selectedFile = ref(null)
const pdfBase64 = ref(null)
const fileInput = ref(null)

const { isLoading, error, result, startImport, reset } = useImport()

const loadingMessage = computed(() => {
  switch (activeMode.value) {
    case 'url':
      return 'Fetching recipe from URL...'
    case 'text':
      return 'Processing recipe text...'
    case 'pdf':
      return 'Extracting recipe from PDF...'
    default:
      return 'Processing...'
  }
})

const isSubmitDisabled = computed(() => {
  if (isLoading.value) return true
  
  switch (activeMode.value) {
    case 'url':
      return !urlInput.value
    case 'text':
      return !textInput.value || textInput.value.length < 50 || textInput.value.length > 50000
    case 'pdf':
      return !pdfBase64.value
    default:
      return true
  }
})

const switchMode = (mode) => {
  // Clear all inputs
  urlInput.value = ''
  textInput.value = ''
  selectedFile.value = null
  pdfBase64.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  
  // Reset form state
  reset()
  
  // Switch mode
  activeMode.value = mode
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  
  if (!file) return
  
  // Validate file type
  if (file.type !== 'application/pdf') {
    error.value = 'Please select a PDF file'
    return
  }
  
  // Validate file size (10MB)
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'File size must be less than 10MB'
    return
  }
  
  selectedFile.value = file
  
  // Convert to base64
  const reader = new FileReader()
  reader.onload = (e) => {
    // Remove data:application/pdf;base64, prefix
    pdfBase64.value = e.target.result.split(',')[1]
  }
  reader.onerror = () => {
    error.value = 'Failed to read file'
  }
  reader.readAsDataURL(file)
}

const clearFile = () => {
  selectedFile.value = null
  pdfBase64.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleSubmit = async () => {
  reset()
  
  let data
  switch (activeMode.value) {
    case 'url':
      if (!urlInput.value) return
      data = urlInput.value
      break
    case 'text':
      if (!textInput.value || textInput.value.length < 50) {
        error.value = 'Please enter at least 50 characters'
        return
      }
      if (textInput.value.length > 50000) {
        error.value = 'Text must be less than 50,000 characters'
        return
      }
      data = textInput.value
      break
    case 'pdf':
      if (!pdfBase64.value) {
        error.value = 'Please select a PDF file'
        return
      }
      data = pdfBase64.value
      break
  }
  
  await startImport(activeMode.value, data)
  
  // Clear input on success
  if (result.value) {
    setTimeout(() => {
      urlInput.value = ''
      textInput.value = ''
      clearFile()
    }, 2000)
  }
}
</script>