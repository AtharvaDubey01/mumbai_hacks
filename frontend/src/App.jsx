import React, { useEffect, useState } from 'react'
import { getClaims, getVerifications, getItems, verifyText } from './api'

export default function App() {
    const [claims, setClaims] = useState([])
    const [vers, setVers] = useState([])
    const [items, setItems] = useState([])

    const [loading, setLoading] = useState(true)
    const [manualText, setManualText] = useState('')
    const [manualResult, setManualResult] = useState(null)
    const [verifying, setVerifying] = useState(false)

    useEffect(() => {
        fetchAll()
        const iv = setInterval(fetchAll, 15000)
        return () => clearInterval(iv)
    }, [])

    async function fetchAll() {
        try {
            const [c, v, i] = await Promise.all([getClaims(), getVerifications(), getItems()])
            setClaims(c)
            setVers(v)
            setItems(i)
            setLoading(false)
        } catch (err) {
            console.error('Error fetching data:', err)
            setLoading(false)
        }
    }

    async function handleVerify() {
        if (!manualText.trim()) return
        setVerifying(true)
        setManualResult(null)
        try {
            const res = await verifyText(manualText)
            setManualResult(res)
        } catch (err) {
            console.error('Verification failed:', err)
        }
        setVerifying(false)
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'false': return 'bg-red-100 text-red-800'
            case 'true': return 'bg-green-100 text-green-800'
            case 'mixture': return 'bg-yellow-100 text-yellow-800'
            default: return 'bg-gray-100 text-gray-800'
        }
    }

    const getVerdictColor = (verdict) => {
        switch (verdict) {
            case 'false': return 'bg-red-500'
            case 'true': return 'bg-green-500'
            case 'mixture': return 'bg-yellow-500'
            default: return 'bg-gray-500'
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
            <div className="container mx-auto px-4 py-8 max-w-7xl">
                {/* Header */}
                <header className="mb-12 text-center">
                    <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        🔍 Misinformation Detection Dashboard
                    </h1>
                    <p className="text-gray-300 text-lg">
                        AI-Powered Autonomous Fact-Checking System
                    </p>
                    <div className="mt-4 flex justify-center gap-4">
                        <div className="bg-purple-500/20 backdrop-blur-sm rounded-lg px-6 py-3 border border-purple-500/30">
                            <div className="text-sm text-gray-400">Claims Tracked</div>
                            <div className="text-2xl font-bold text-purple-300">{claims.length}</div>
                        </div>
                        <div className="bg-pink-500/20 backdrop-blur-sm rounded-lg px-6 py-3 border border-pink-500/30">
                            <div className="text-sm text-gray-400">Verifications</div>
                            <div className="text-2xl font-bold text-pink-300">{vers.length}</div>
                        </div>
                        <div className="bg-blue-500/20 backdrop-blur-sm rounded-lg px-6 py-3 border border-blue-500/30">
                            <div className="text-sm text-gray-400">Sources</div>
                            <div className="text-2xl font-bold text-blue-300">{items.length}</div>
                        </div>
                    </div>
                </header>

                {/* Manual Verification Section */}
                <section className="mb-12 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700/50 shadow-2xl max-w-3xl mx-auto">
                    <h2 className="text-2xl font-bold mb-6 text-blue-300 flex items-center gap-2">
                        <span>🕵️</span> Check a Fact
                    </h2>
                    <div className="flex gap-4 mb-6">
                        <textarea
                            className="flex-1 bg-gray-900/50 border border-gray-700 rounded-xl p-4 text-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none h-24"
                            placeholder="Enter a claim to verify (e.g., 'The earth is flat')..."
                            value={manualText}
                            onChange={(e) => setManualText(e.target.value)}
                        />
                        <button
                            onClick={handleVerify}
                            disabled={verifying || !manualText.trim()}
                            className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-8 rounded-xl font-bold transition-all duration-300 flex items-center justify-center min-w-[120px]"
                        >
                            {verifying ? (
                                <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-white"></div>
                            ) : (
                                'Verify'
                            )}
                        </button>
                    </div>

                    {manualResult && (
                        <div className="bg-gray-900/80 rounded-xl p-6 border border-gray-700 animate-fade-in">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className={`w-4 h-4 rounded-full ${getVerdictColor(manualResult.verdict)}`}></div>
                                    <span className={`text-xl font-bold ${manualResult.verdict === 'false' ? 'text-red-400' : manualResult.verdict === 'true' ? 'text-green-400' : 'text-yellow-400'}`}>
                                        {manualResult.verdict.toUpperCase()}
                                    </span>
                                </div>
                                <span className="text-gray-400">
                                    Confidence: <span className="text-blue-300 font-bold">{(manualResult.score * 100).toFixed(0)}%</span>
                                </span>
                            </div>

                            {manualResult.summary && (
                                <div className="mb-4 bg-blue-900/30 p-4 rounded-lg border border-blue-500/30">
                                    <div className="text-sm text-blue-300 font-bold mb-1">Summary:</div>
                                    <p className="text-gray-200 text-sm leading-relaxed">
                                        {manualResult.summary}
                                    </p>
                                </div>
                            )}

                            {manualResult.reasons && manualResult.reasons.length > 0 && (
                                <div className="mb-4">
                                    <div className="text-sm text-gray-500 mb-2">Analysis:</div>
                                    <ul className="list-disc list-inside text-gray-300 space-y-1">
                                        {manualResult.reasons.map((r, i) => (
                                            <li key={i}>{r}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {manualResult.evidence && manualResult.evidence.length > 0 && (
                                <div>
                                    <div className="text-sm text-gray-500 mb-2">Evidence:</div>
                                    <div className="space-y-2">
                                        {manualResult.evidence.slice(0, 3).map((e, idx) => (
                                            <a
                                                key={idx}
                                                href={e.link}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="block bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition-colors border border-gray-700 hover:border-blue-500/30"
                                            >
                                                <div className="text-blue-400 font-medium text-sm line-clamp-1">{e.title}</div>
                                                <div className="text-gray-500 text-xs line-clamp-1 mt-1">{e.snippet}</div>
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </section>

                {loading ? (
                    <div className="text-center py-20">
                        <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-500"></div>
                        <p className="mt-4 text-gray-400">Loading data...</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Claims Section */}
                        <section className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50 shadow-2xl">
                            <h2 className="text-2xl font-bold mb-6 text-purple-300 flex items-center gap-2">
                                <span>📋</span> Recent Claims
                            </h2>
                            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                                {claims.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">
                                        No claims detected yet. Agents will start collecting data soon.
                                    </div>
                                ) : (
                                    claims.map(claim => (
                                        <div key={claim._id} className="bg-gray-900/50 rounded-xl p-4 border border-gray-700/30 hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20">
                                            <div className="text-xs text-gray-500 mb-2">
                                                {new Date(claim.extracted_at).toLocaleString()}
                                            </div>
                                            <div className="text-gray-200 leading-relaxed mb-3">
                                                {claim.text}
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <span className={`text-xs px-3 py-1 rounded-full font-medium ${getStatusColor(claim.status)}`}>
                                                    {claim.status.toUpperCase()}
                                                </span>
                                                <span className="text-xs text-gray-500">
                                                    ID: {claim._id.slice(-6)}
                                                </span>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </section>

                        {/* Verifications Section */}
                        <section className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50 shadow-2xl">
                            <h2 className="text-2xl font-bold mb-6 text-pink-300 flex items-center gap-2">
                                <span>✅</span> Verifications
                            </h2>
                            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                                {vers.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">
                                        No verifications yet. The verifier agent will process claims automatically.
                                    </div>
                                ) : (
                                    vers.map(v => (
                                        <div key={v._id} className="bg-gray-900/50 rounded-xl p-4 border border-gray-700/30 hover:border-pink-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-pink-500/20">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className={`w-3 h-3 rounded-full ${getVerdictColor(v.verdict)}`}></div>
                                                <span className="text-xs text-gray-500">
                                                    {new Date(v.checked_at).toLocaleString()}
                                                </span>
                                            </div>
                                            <div className="mb-3">
                                                <span className="text-sm text-gray-400">Verdict: </span>
                                                <span className={`font-bold ${v.verdict === 'false' ? 'text-red-400' : v.verdict === 'true' ? 'text-green-400' : 'text-yellow-400'}`}>
                                                    {v.verdict.toUpperCase()}
                                                </span>
                                                <span className="text-sm text-gray-400 ml-3">
                                                    Confidence: <span className="font-bold text-purple-300">{(v.score * 100).toFixed(0)}%</span>
                                                </span>
                                            </div>
                                            {v.evidence && v.evidence.length > 0 && (
                                                <div className="mt-3 border-t border-gray-700 pt-3">
                                                    <div className="text-xs text-gray-400 mb-2">Evidence Sources:</div>
                                                    <ul className="space-y-1">
                                                        {v.evidence.slice(0, 3).map((e, idx) => (
                                                            <li key={idx} className="text-xs">
                                                                <a
                                                                    href={e.link}
                                                                    target="_blank"
                                                                    rel="noreferrer"
                                                                    className="text-blue-400 hover:text-blue-300 hover:underline line-clamp-1"
                                                                >
                                                                    🔗 {e.title || e.snippet || e.link}
                                                                </a>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        </section>
                    </div>
                )}

                {/* Footer */}
                <footer className="mt-12 text-center text-gray-500 text-sm">
                    <p>Powered by Advanced Agentic AI • Auto-refreshes every 15 seconds</p>
                </footer>
            </div>
        </div>
    )
}
