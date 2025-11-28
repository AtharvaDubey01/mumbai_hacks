import React, { useEffect, useState } from 'react'
import { getClaims, getVerifications, getItems } from './api'

export default function App() {
    const [claims, setClaims] = useState([])
    const [vers, setVers] = useState([])
    const [items, setItems] = useState([])
    const [loading, setLoading] = useState(true)

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
