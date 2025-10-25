import { useState } from 'react'

interface Config {
  target_os: 'Rocky9' | 'Ubuntu25.04'
  generate_passwords: boolean
  values: Record<string, any>
}

export function ConfigSection() {
  const [config, setConfig] = useState<Config | null>(null)
  const [targetOS, setTargetOS] = useState<'Rocky9' | 'Ubuntu25.04'>('Rocky9')
  const [generatePasswords, setGeneratePasswords] = useState(true)
  const [customValues, setCustomValues] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const getConfig = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/v1/config')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setConfig(data)
      setTargetOS(data.target_os)
      setGeneratePasswords(data.generate_passwords)
      setCustomValues(JSON.stringify(data.values, null, 2))
    } catch (error) {
      console.error('Failed to fetch config:', error)
      setError('Failed to connect to backend. Make sure the server is running on localhost:8000')
    }
    setLoading(false)
  }

  const updateConfig = async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      let parsedValues = {}
      if (customValues.trim()) {
        try {
          parsedValues = JSON.parse(customValues)
        } catch (e) {
          throw new Error('Invalid JSON in custom values')
        }
      }

      const newConfig = {
        target_os: targetOS,
        generate_passwords: generatePasswords,
        values: parsedValues,
      }

      const response = await fetch('/api/v1/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfig),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setConfig(data)
      setSuccess('Configuration updated successfully')
    } catch (error: any) {
      console.error('Failed to update config:', error)
      setError(error.message || 'Failed to update configuration')
    }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Configuration</h2>

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
        {/* Get Configuration */}
        <div className="border border-slate-200 rounded-lg p-6 bg-white shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Get Configuration</h3>
          <button
            onClick={getConfig}
            disabled={loading}
            className="w-full px-4 py-2 bg-slate-900 text-white rounded-md hover:bg-slate-800 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
          >
            {loading ? 'Loading...' : 'Get Configuration'}
          </button>
        </div>

        {/* Update Configuration */}
        <div className="border border-slate-200 rounded-lg p-6 bg-white shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Update Configuration</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Target OS
              </label>
              <select
                value={targetOS}
                onChange={(e) => setTargetOS(e.target.value as 'Rocky9' | 'Ubuntu25.04')}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              >
                <option value="Rocky9">Rocky 9</option>
                <option value="Ubuntu25.04">Ubuntu 25.04</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="generate-passwords"
                checked={generatePasswords}
                onChange={(e) => setGeneratePasswords(e.target.checked)}
                className="w-4 h-4 text-slate-900 border-slate-300 rounded focus:ring-slate-900"
              />
              <label htmlFor="generate-passwords" className="text-sm text-slate-700">
                Generate passwords automatically
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Custom Values (JSON)
              </label>
              <textarea
                value={customValues}
                onChange={(e) => setCustomValues(e.target.value)}
                placeholder='{"key": "value"}'
                rows={4}
                className="w-full px-3 py-2 border border-slate-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>

            <button
              onClick={updateConfig}
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
            >
              {loading ? 'Updating...' : 'Update Configuration'}
            </button>
          </div>
        </div>
      </div>

      {/* Current Configuration Display */}
      {config && (
        <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">Current Configuration</h3>
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
    </div>
  )
}
