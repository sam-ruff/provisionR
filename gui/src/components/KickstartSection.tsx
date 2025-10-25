import { useState } from 'react'

export function KickstartSection() {
  const [template, setTemplate] = useState<string | null>(null)
  const [renderedKickstart, setRenderedKickstart] = useState<string | null>(null)
  const [templateName, setTemplateName] = useState('default')
  const [uploadTemplateName, setUploadTemplateName] = useState('')
  const [useAsDefault, setUseAsDefault] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const getTemplate = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/v1/templates/${templateName}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.text()
      setTemplate(data)
    } catch (error) {
      console.error('Failed to fetch template:', error)
      setError(`Failed to fetch template '${templateName}'`)
    }
    setLoading(false)
  }

  const uploadTemplate = async () => {
    if (!selectedFile || !uploadTemplateName) {
      setError('Please select a file and provide a template name')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('template_name', uploadTemplateName)
      formData.append('use_as_default', useAsDefault.toString())

      const response = await fetch('/api/v1/templates', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setSuccess(data.message)
      setUploadTemplateName('')
      setUseAsDefault(false)
      setSelectedFile(null)
      // Reset file input
      const fileInput = document.getElementById('template-file') as HTMLInputElement
      if (fileInput) fileInput.value = ''
    } catch (error) {
      console.error('Failed to upload template:', error)
      setError('Failed to upload template')
    }
    setLoading(false)
  }

  const renderTemplate = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/v1/ks?mac=00:11:22:33:44:55&uuid=test-uuid-12345&serial=TEST-SN-001&template_name=${templateName}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.text()
      setRenderedKickstart(data)
    } catch (error) {
      console.error('Failed to render template:', error)
      setError(`Failed to render template '${templateName}'`)
    }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Kickstart Templates</h2>

      {error && (
        <div className="border border-red-200 rounded-lg p-4 bg-red-50 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-800">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-600 transition-colors"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {success && (
        <div className="border border-green-200 rounded-lg p-4 bg-green-50 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-green-800">{success}</p>
            </div>
            <button
              onClick={() => setSuccess(null)}
              className="text-green-400 hover:text-green-600 transition-colors"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Get Template */}
        <div className="border border-slate-200 rounded-lg p-6 bg-white shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Get Template</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Template Name
              </label>
              <input
                type="text"
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                placeholder="default"
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={getTemplate}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-slate-900 text-white rounded-md hover:bg-slate-800 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
              >
                {loading ? 'Loading...' : 'Get Template'}
              </button>
              <button
                onClick={renderTemplate}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
              >
                {loading ? 'Rendering...' : 'Render Template'}
              </button>
            </div>
          </div>
        </div>

        {/* Upload Template */}
        <div className="border border-slate-200 rounded-lg p-6 bg-white shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Upload Template</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Template Name
              </label>
              <input
                type="text"
                value={uploadTemplateName}
                onChange={(e) => setUploadTemplateName(e.target.value)}
                placeholder="my-template"
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Template File
              </label>
              <input
                id="template-file"
                type="file"
                accept=".j2,.jinja2,.ks"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="use-as-default"
                checked={useAsDefault}
                onChange={(e) => setUseAsDefault(e.target.checked)}
                className="w-4 h-4 text-slate-900 border-slate-300 rounded focus:ring-slate-900"
              />
              <label htmlFor="use-as-default" className="text-sm text-slate-700">
                Use as default template
              </label>
            </div>
            <button
              onClick={uploadTemplate}
              disabled={loading || !selectedFile || !uploadTemplateName}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-green-600 focus:ring-offset-2"
            >
              {loading ? 'Uploading...' : 'Upload Template'}
            </button>
          </div>
        </div>
      </div>

      {/* Template Content */}
      {template && (
        <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">Template Content</h3>
            <button
              onClick={() => setTemplate(null)}
              className="text-slate-400 hover:text-slate-600 transition-colors"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <pre className="text-sm bg-slate-900 text-slate-100 p-4 rounded overflow-auto font-mono max-h-96">
            {template}
          </pre>
        </div>
      )}

      {/* Rendered Kickstart */}
      {renderedKickstart && (
        <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">Rendered Kickstart</h3>
            <button
              onClick={() => setRenderedKickstart(null)}
              className="text-slate-400 hover:text-slate-600 transition-colors"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <pre className="text-sm bg-slate-900 text-slate-100 p-4 rounded overflow-auto font-mono max-h-96">
            {renderedKickstart}
          </pre>
        </div>
      )}
    </div>
  )
}
