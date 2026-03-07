import { ref } from 'vue'
import { useApi } from './useApi'

export function useImport() {
  const { createImport, getImportStatus } = useApi()
  
  const isLoading = ref(false)
  const error = ref(null)
  const result = ref(null)
  
  const pollInterval = ref(null)
  
  const startImport = async (url) => {
    isLoading.value = true
    error.value = null
    result.value = null
    
    try {
      // Create import job
      const response = await createImport(url)
      const jobId = response.job_id
      
      // Start polling for status
      pollInterval.value = setInterval(async () => {
        try {
          const status = await getImportStatus(jobId)
          
          if (status.status === 'completed') {
            clearInterval(pollInterval.value)
            isLoading.value = false
            result.value = {
              filename: status.filename,
              message: `Recipe imported successfully: ${status.filename}`
            }
          } else if (status.status === 'failed') {
            clearInterval(pollInterval.value)
            isLoading.value = false
            error.value = status.error || 'Import failed'
          }
          // Continue polling if status is 'pending' or 'processing'
        } catch (err) {
          clearInterval(pollInterval.value)
          isLoading.value = false
          error.value = 'Failed to check import status'
        }
      }, 1000) // Poll every second
      
    } catch (err) {
      isLoading.value = false
      error.value = err.response?.data?.detail || 'Failed to start import'
    }
  }
  
  const reset = () => {
    if (pollInterval.value) {
      clearInterval(pollInterval.value)
    }
    isLoading.value = false
    error.value = null
    result.value = null
  }
  
  return {
    isLoading,
    error,
    result,
    startImport,
    reset
  }
}
