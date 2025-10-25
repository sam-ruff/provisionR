import { useState } from 'react'
import { KickstartSection } from './components/KickstartSection'
import { ConfigSection } from './components/ConfigSection'

function App() {
  const [targetOS] = useState<'Rocky9' | 'Ubuntu25.04'>('Rocky9')

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

        {/* Kickstart Templates Section */}
        <div className="mb-12">
          <KickstartSection />
        </div>

        {/* Configuration Section */}
        <div className="mb-12">
          <ConfigSection />
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
