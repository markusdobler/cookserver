<template>
  <div class="max-w-2xl mx-auto p-6">
    <div class="bg-base2 rounded-lg shadow-lg p-8">
      <h2 class="text-3xl font-bold text-base01 mb-6">Import Recipe</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label for="url" class="block text-sm font-medium text-base01 mb-2">
            Recipe URL
          </label>
          <input
            id="url"
            v-model="url"
            type="url"
            required
            placeholder="https://example.com/recipe"
            class="w-full px-4 py-3 bg-base3 border-2 border-base1 rounded-lg focus:outline-none focus:border-blue text-base00 placeholder-base1"
            :disabled="isLoading"
          />
        </div>
        
        <button
          type="submit"
          :disabled="isLoading || !url"
          class="w-full py-3 px-6 rounded-lg font-semibold text-base3 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :class="isLoading ? 'bg-base1' : 'bg-blue hover:bg-cyan'"
        >
          <span v-if="isLoading">Importing...</span>
          <span v-else>Import Recipe</span>
        </button>
      </form>
      
      <!-- Success Message -->
      <div
        v-if="result"
        class="mt-6 p-4 bg-green bg-opacity-10 border-2 border-green rounded-lg"
      >
        <p class="text-green font-semibold">✓ {{ result.message }}</p>
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
        <p class="mt-2 text-base01">Processing your recipe...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useImport } from '../../composables/useImport'

const url = ref('')
const { isLoading, error, result, startImport, reset } = useImport()

const handleSubmit = async () => {
  if (!url.value) return
  
  reset()
  await startImport(url.value)
  
  // Clear URL on success
  if (result.value) {
    setTimeout(() => {
      url.value = ''
    }, 2000)
  }
}
</script>
