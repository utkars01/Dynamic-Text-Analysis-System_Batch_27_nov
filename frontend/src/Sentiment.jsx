import { useState } from 'react'

const Sentiment = ({ data }) => {
    const getSentimentColor = (label) => {
        if (label === 'Positive') return 'bg-green-600'
        if (label === 'Negative') return 'bg-red-600'
        return 'bg-yellow-600'
    }

    return (
        <div>
            <div className="mb-6">
                <h2 className="text-3xl font-extrabold bg-gradient-to-r from-blue-400 to-blue-200 bg-clip-text text-transparent mb-2">
                    💭 Sentiment Analysis
                </h2>
                <p className="text-sm text-gray-400">Advanced emotional tone detection using VADER</p>
            </div>
            {data ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="text-center p-6 bg-gray-900/50 rounded-xl border border-gray-700">
                        <div className="mb-3">
                            <h4 className="text-lg font-bold text-white mb-1">Overall Sentiment</h4>
                            <p className="text-xs text-gray-400">Aggregated sentiment classification</p>
                        </div>
                        <div className={`inline-block px-6 py-3 rounded-lg ${getSentimentColor(data.label)} text-white font-bold text-2xl`}>
                            {data.label}
                        </div>
                        <p className="text-sm text-gray-400 mt-3">Compound Score: {data.compound.toFixed(3)}</p>
                    </div>
                    <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-700">
                        <div className="mb-4">
                            <h4 className="text-lg font-bold text-white mb-1">Sentiment Distribution</h4>
                            <p className="text-xs text-gray-400">Detailed probability breakdown</p>
                        </div>
                        <div className="space-y-2">
                            <div>
                                <div className="flex justify-between text-xs text-gray-400 mb-1">
                                    <span className="font-medium">Positive</span>
                                    <span className="font-bold">{(data.positive * 100).toFixed(0)}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div className="bg-green-500 h-2 rounded-full" style={{ width: `${data.positive * 100}%` }}></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-xs text-gray-400 mb-1">
                                    <span className="font-medium">Neutral</span>
                                    <span className="font-bold">{(data.neutral * 100).toFixed(0)}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${data.neutral * 100}%` }}></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-xs text-gray-400 mb-1">
                                    <span className="font-medium">Negative</span>
                                    <span className="font-bold">{(data.negative * 100).toFixed(0)}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div className="bg-red-500 h-2 rounded-full" style={{ width: `${data.negative * 100}%` }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <p className="text-gray-400">Loading sentiment analysis...</p>
            )}
        </div>
    )
}

export default Sentiment