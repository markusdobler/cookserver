import axios from 'axios'

const basePath = import.meta.env.VITE_BASE_PATH || ''

const api = axios.create({
  baseURL: basePath,
  headers: {
    'Content-Type': 'application/json'
  }
})

export function useApi() {
  const createImport = async (request) => {
    // request can be:
    // { type: 'url', url: 'https://...' }
    // { type: 'text', text: '...' }
    // { type: 'pdf', pdf_data: 'base64...' }
    const response = await api.post('/api/import', request)
    return response.data
  }

  const getImportStatus = async (jobId) => {
    const response = await api.get(`/api/import/${jobId}`)
    return response.data
  }

  return {
    createImport,
    getImportStatus
  }
}
