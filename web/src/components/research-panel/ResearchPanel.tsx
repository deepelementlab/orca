'use client'

import { useState } from 'react'

const WORKFLOWS = [
  { id: 'deep_research', name: 'Deep Research', icon: '🔬', desc: 'Multi-round recursive search' },
  { id: 'lit_review', name: 'Literature Review', icon: '📚', desc: 'Structured literature survey' },
  { id: 'paper_audit', name: 'Paper Audit', icon: '🔍', desc: 'Code/method/result audit' },
  { id: 'source_compare', name: 'Source Compare', icon: '⚖️', desc: 'Multi-source comparison' },
  { id: 'peer_review', name: 'Peer Review', icon: '📝', desc: 'Structured peer review' },
  { id: 'paper_writing', name: 'Paper Writing', icon: '✍️', desc: 'Paper draft generation' },
  { id: 'replication', name: 'Replication', icon: '🔄', desc: 'Experiment replication plan' },
  { id: 'eli5', name: 'ELI5', icon: '💡', desc: 'Simple explanations' },
  { id: 'session_search', name: 'Session Search', icon: '🔎', desc: 'Search past sessions' },
]

export default function ResearchPanel() {
  const [query, setQuery] = useState('')
  const [workflow, setWorkflow] = useState('deep_research')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [sources, setSources] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleResearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    setSources([])

    try {
      const res = await fetch(`${API_BASE}/api/research/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow, query, depth: 2, max_sources: 10 }),
      })
      const data = await res.json()
      setSessionId(data.session_id)

      // Poll for results
      const poll = async () => {
        const statusRes = await fetch(`${API_BASE}/api/research/sessions/${data.session_id}`)
        const statusData = await statusRes.json()
        if (statusData.status === 'complete') {
          setResult(statusData.result?.summary || 'No summary')
          setSources(statusData.result?.sources || [])
          setLoading(false)
        } else if (statusData.status === 'failed') {
          setError(statusData.error || 'Research failed')
          setLoading(false)
        } else {
          setTimeout(poll, 2000)
        }
      }
      setTimeout(poll, 2000)
    } catch (err: any) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Workflow Selector */}
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-3 lg:grid-cols-3">
        {WORKFLOWS.map((wf) => (
          <button
            key={wf.id}
            onClick={() => setWorkflow(wf.id)}
            className={`rounded-lg border p-3 text-left transition-all ${
              workflow === wf.id
                ? 'border-orca-500 bg-orca-500/10 text-white'
                : 'border-[#2e2e2e] bg-[#141414] text-gray-400 hover:border-gray-500'
            }`}
          >
            <div className="text-lg">{wf.icon}</div>
            <div className="mt-1 text-sm font-medium">{wf.name}</div>
            <div className="text-xs text-gray-500">{wf.desc}</div>
          </button>
        ))}
      </div>

      {/* Query Input */}
      <div className="flex gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleResearch()}
          placeholder="Enter your research query..."
          className="flex-1 rounded-lg border border-[#2e2e2e] bg-[#141414] px-4 py-3 text-white placeholder-gray-500 focus:border-orca-500 focus:outline-none"
        />
        <button
          onClick={handleResearch}
          disabled={loading || !query.trim()}
          className="rounded-lg bg-orca-500 px-6 py-3 font-medium text-white transition-colors hover:bg-orca-600 disabled:opacity-50"
        >
          {loading ? 'Researching...' : 'Research'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-800 bg-red-900/20 p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center gap-3 text-gray-400">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-orca-500 border-t-transparent" />
          <span>Running {WORKFLOWS.find(w => w.id === workflow)?.name}...</span>
          {sessionId && <span className="text-xs text-gray-600">({sessionId})</span>}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="rounded-lg border border-[#2e2e2e] bg-[#141414] p-6">
          <h3 className="mb-4 text-lg font-semibold text-orca-500">Results</h3>
          <div className="prose prose-invert max-w-none whitespace-pre-wrap text-gray-300">
            {result}
          </div>
        </div>
      )}

      {/* Sources */}
      {sources.length > 0 && (
        <div className="rounded-lg border border-[#2e2e2e] bg-[#141414] p-6">
          <h3 className="mb-4 text-lg font-semibold text-gray-300">
            Sources ({sources.length})
          </h3>
          <div className="space-y-2">
            {sources.map((src, i) => (
              <div key={i} className="flex items-start gap-2 rounded border border-[#2e2e2e] p-3">
                <span className="text-xs text-gray-500">[{i + 1}]</span>
                <div className="flex-1">
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-orca-500 hover:underline"
                  >
                    {src.title}
                  </a>
                  <div className="text-xs text-gray-500">
                    {src.authors?.slice(0, 3).join(', ')}
                    {src.citation_count ? ` · ${src.citation_count} citations` : ''}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
