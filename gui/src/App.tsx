import { useState } from 'react'

function App() {
  const [config, setConfig] = useState<any>(null)
  const [kickstart, setKickstart] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingKickstart, setLoadingKickstart] = useState(false)
  const [targetOS] = useState<'Rocky9' | 'Ubuntu25.04'>('Rocky9')
  const [error, setError] = useState<string | null>(null)

  const fetchConfig = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/v1/config')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setConfig(data)
    } catch (error) {
      console.error('Failed to fetch config:', error)
      setError('Failed to connect to backend. Make sure the server is running on localhost:8000')
    }
    setLoading(false)
  }

  const generateTestKickstart = async () => {
    setLoadingKickstart(true)
    setError(null)
    try {
      const response = await fetch('/api/v1/ks?mac=00:11:22:33:44:55&uuid=test-uuid-12345&serial=TEST-SN-001')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.text()
      setKickstart(data)
    } catch (error) {
      console.error('Failed to generate kickstart:', error)
      setError('Failed to generate kickstart. Make sure the backend is running on localhost:8000')
    }
    setLoadingKickstart(false)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* OS Selector in top left */}
      <div className="fixed top-4 left-4">
        <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-slate-700">Target OS:</span>
            <div className="relative inline-flex items-center">
              <button
                disabled
                className={`px-3 py-1 text-sm font-medium rounded-l-md transition-colors ${
                  targetOS === 'Rocky9'
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-400'
                } cursor-not-allowed`}
              >
                Rocky 9
              </button>
              <button
                disabled
                className={`px-3 py-1 text-sm font-medium rounded-r-md transition-colors ${
                  targetOS === 'Ubuntu25.04'
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-400'
                } cursor-not-allowed`}
              >
                Ubuntu 25.04
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto p-8 pt-24">
        <h1 className="text-4xl font-bold mb-8 text-slate-900">provisionR</h1>
        <p className="text-slate-600 mb-8">
          Generate Kickstart files with automatic password management
        </p>

        <div className="space-y-4">
          <div className="flex gap-3">
            <button
              onClick={fetchConfig}
              disabled={loading}
              className="px-4 py-2 bg-slate-900 text-white rounded-md hover:bg-slate-800 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
            >
              {loading ? 'Loading...' : 'Get Configuration'}
            </button>

            <button
              onClick={generateTestKickstart}
              disabled={loadingKickstart}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
            >
              {loadingKickstart ? 'Generating...' : 'Generate Test Kickstart'}
            </button>
          </div>

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

          {config && (
            <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Current Configuration</h2>
                <button
                  onClick={() => setConfig(null)}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                  aria-label="Close"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <pre className="text-sm bg-slate-100 p-4 rounded overflow-auto">
                {JSON.stringify(config, null, 2)}
              </pre>
            </div>
          )}

          {kickstart && (
            <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Generated Kickstart</h2>
                <button
                  onClick={() => setKickstart(null)}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                  aria-label="Close"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <pre className="text-sm bg-slate-900 text-slate-100 p-4 rounded overflow-auto font-mono">
                {kickstart}
              </pre>
            </div>
          )}
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <a
            href={import.meta.env.DEV ? 'http://localhost:8000/docs' : '/docs'}
            target="_blank"
            rel="noopener noreferrer"
            className="border border-slate-200 rounded-lg p-6 bg-white shadow-sm hover:shadow-md hover:border-slate-300 transition-all cursor-pointer"
          >
            <h3 className="text-lg font-semibold mb-2 text-blue-600">Swagger Docs</h3>
            <p className="text-sm text-slate-600">
              View interactive API documentation
            </p>
          </a>

          <div className="border border-slate-200 rounded-lg p-6 bg-white shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Kickstart Generation</h3>
            <p className="text-sm text-slate-600">
              Generate kickstart files with machine-specific parameters
            </p>
          </div>

          <div className="border border-slate-200 rounded-lg p-6 bg-white shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Password Management</h3>
            <p className="text-sm text-slate-600">
              Automatic password generation and persistence
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
