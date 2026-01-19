import { useState } from 'react'

const Topic = ({ data }) => {
    return (
        <div>
            <div className="mb-6">
                <h2 className="text-3xl font-extrabold bg-gradient-to-r from-purple-400 to-purple-200 bg-clip-text text-transparent mb-2">
                    Topic Analysis
                </h2>
                <p className="text-sm text-gray-400">AI-powered theme identification and keyword extraction</p>
            </div>
            {data ? (
                <div className="space-y-6">
                    <div className="text-center p-6 bg-purple-900/30 rounded-xl border border-purple-500/50">
                        <p className="text-xs text-gray-400 uppercase tracking-widest mb-2 font-semibold">Detected Theme</p>
                        <h3 className="text-3xl font-bold text-purple-300 mb-2">{data.label}</h3>
                        <p className="text-sm text-purple-400">{data.key}</p>
                        <p className="text-xs text-gray-500 mt-2">Confidence: {(data.score * 100).toFixed(1)}%</p>
                    </div>

                    {data.wordcloud && (
                        <div>
                            <div className="mb-4 ">
                                <h4 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                                    <span className="text-2xl">Topic Word Cloud</span>
                                </h4>
                                <p className="text-xs text-gray-400">Visual representation of key terms contributing to the theme</p>
                            </div>
                            <div className="bg-[#1e1b4b] rounded-xl p-4 border border-purple-500/30">
                                <img
                                    src={`data:image/png;base64,${data.wordcloud}`}
                                    alt="Word Cloud"
                                    className="w-full h-auto rounded-lg"
                                />
                            </div>
                        </div>
                    )}

                    {data.distribution && data.distribution.length > 0 && (
                        <div>
                            <div className="mb-4">
                                <h4 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                                    <span className="text-2xl">Theme Prevalence</span>
                                </h4>
                                <p className="text-xs text-gray-400">Relevance scores across top 5 dominant themes</p>
                            </div>
                            <div className="space-y-3">
                                {data.distribution.map((topic, index) => (
                                    <div key={index}>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-300 font-medium">{topic.label}</span>
                                            <span className="text-purple-400 font-bold">{topic.score.toFixed(3)}</span>
                                        </div>
                                        <div className="w-full bg-gray-700 rounded-full h-3">
                                            <div
                                                className="bg-purple-500 h-3 rounded-full transition-all duration-500"
                                                style={{ width: `${(topic.score / Math.max(...data.distribution.map(t => t.score))) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <p className="text-gray-400">Loading topic analysis...</p>
            )}
        </div>
    )
}

export default Topic