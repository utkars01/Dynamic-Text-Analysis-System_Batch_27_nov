import { useState } from 'react'

const Summary = ({ data }) => {
    const [copied, setCopied] = useState(false)

    const handleCopy = () => {
        navigator.clipboard.writeText(data)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div>
            <div className="mb-6">
                <h2 className="text-3xl font-extrabold bg-gradient-to-r from-teal-400 to-teal-200 bg-clip-text text-transparent mb-2">
                    AI Summary Generation
                </h2>
                <p className="text-sm text-gray-400">Neural abstractive summarization with BART</p>
            </div>
            {data ? (
                <>
                    <div className="p-6 bg-teal-900/20 rounded-xl border-l-4 border-teal-500">
                        <div className="mb-3">
                            <p className="text-sm text-teal-400 uppercase tracking-widest font-bold flex items-center gap-2">
                                <span>✨</span>
                                Generated Summary
                            </p>
                        </div>
                        <p className="text-gray-200 leading-relaxed text-base">{data}</p>
                    </div>

                    <div className="flex gap-3 mt-4 justify-center">
                        <button
                            onClick={handleCopy}
                            className="px-4 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2 hover:scale-105 active:scale-95"
                        >
                            {copied ? (
                                <>
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                    Copied!
                                </>
                            ) : (
                                <>
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                    </svg>
                                    Copy Summary
                                </>
                            )}
                        </button>
                    </div>
                </>
            ) : (
                <p className="text-gray-400">Loading summary...</p>
            )}
        </div>
    )
}

export default Summary