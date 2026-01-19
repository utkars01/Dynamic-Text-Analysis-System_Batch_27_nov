import { useState } from 'react'
import Topic from './Topic'
import Sentiment from './Sentiment'
import Summary from './Summary'

function App() {
  const [pastedText, setPastedText] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [showResults, setShowResults] = useState(false)
  const [loading, setLoading] = useState(false)
  const [topicData, setTopicData] = useState(null)
  const [sentimentData, setSentimentData] = useState(null)
  const [summaryData, setSummaryData] = useState(null)

  const handleTextChange = (e) => {
    const text = e.target.value
    setPastedText(text)
    if (text && uploadedFile) {
      setUploadedFile(null)
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      const validTypes = [
        'text/plain',
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
      ]
      if (validTypes.includes(file.type)) {
        setUploadedFile(file)
        if (pastedText) {
          setPastedText('')
        }
      } else {
        alert('Please upload a valid file (.txt, .docx, or .pdf)')
      }
    }
  }

  const handleClearFile = () => {
    setUploadedFile(null)
  }

  const handleSummarize = async () => {
    if (!pastedText && !uploadedFile) {
      alert('Please paste text or upload a file to summarize')
      return
    }

    setLoading(true)
    setTopicData(null)
    setSentimentData(null)
    setSummaryData(null)
    setShowResults(true)

    try {
      let textToAnalyze = pastedText

      if (uploadedFile) {
        const formData = new FormData()
        formData.append('file', uploadedFile)
        const uploadResponse = await fetch('http://localhost:8000/api/upload', {
          method: 'POST',
          body: formData
        })
        if (!uploadResponse.ok) throw new Error('File upload failed')
        const uploadData = await uploadResponse.json()
        textToAnalyze = uploadData.text
      }

      const requestBody = JSON.stringify({ text: textToAnalyze })
      const headers = { 'Content-Type': 'application/json' }

      await Promise.all([
        fetch('http://localhost:8000/api/topic', { method: 'POST', headers, body: requestBody })
          .then(res => res.json())
          .then(data => setTopicData(data))
          .catch(err => console.error('Topic error:', err)),
        fetch('http://localhost:8000/api/sentiment', { method: 'POST', headers, body: requestBody })
          .then(res => res.json())
          .then(data => setSentimentData(data))
          .catch(err => console.error('Sentiment error:', err)),
        fetch('http://localhost:8000/api/summary', { method: 'POST', headers, body: requestBody })
          .then(res => res.json())
          .then(data => setSummaryData(data.summary))
          .catch(err => console.error('Summary error:', err))
      ]).finally(() => setLoading(false))
    } catch (error) {
      alert('Error: ' + error.message)
      setLoading(false)
    }
  }

  const handleBackToInput = () => {
    setShowResults(false)
  }

  return (
    <>
      {showResults && (
        <div className="fixed top-0 left-0 right-0 z-50">
          <nav className="navbar bg-slate-500/20 backdrop-blur-xl rounded-3xl border border-white/20 p-4 m-4 h-16 flex items-center justify-center">
            <ul className="flex space-x-16 text-white font-medium">
              <li><a href="#topic" className="hover:text-gray-200 transition cursor-pointer">Topic</a></li>
              <li><a href="#sentiment" className="hover:text-gray-200 transition cursor-pointer">Sentiment</a></li>
              <li><a href="#summary" className="hover:text-gray-200 transition cursor-pointer">Summary</a></li>
            </ul>
          </nav>
        </div>
      )}

      <div className={`min-h-screen pb-12 px-4 flex items-center ${showResults ? 'pt-28' : 'pt-12'}`}>
        <div className="max-w-7xl mx-auto w-full">
          {!showResults ? (
            <>
              <div className="text-center mb-6">
                <h1 className="text-5xl md:text-6xl font-bold text-white mb-3 bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
                  News <span className="text-red-500">Summarizer.</span>
                </h1>
                <p className="text-xl text-gray-300 mb-2">
                  Summarize the news in seconds
                </p>
                <p className="text-xs text-gray-500 max-w-2xl mx-auto">
                  Paste your article or upload a document to get instant topic analysis, sentiment insights, and concise summaries
                </p>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div className="flex flex-col">
                  <label className="text-white text-base font-semibold mb-2">
                    Paste Your Text
                  </label>
                  <textarea
                    value={pastedText}
                    onChange={handleTextChange}
                    disabled={!!uploadedFile}
                    placeholder="Paste your news article here..."
                    className={`w-full h-56 p-4 border-2 border-white/20 bg-white/10 backdrop-blur-sm rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:border-white/40 focus:bg-white/15 transition resize-none ${uploadedFile ? 'opacity-50 cursor-not-allowed' : ''}`}
                  />
                </div>
                <div className="flex flex-col">
                  <label className="text-white text-base font-semibold mb-2">
                    Upload Document
                  </label>
                  <label className={`flex flex-col items-center justify-center w-full h-56 border-2 border-dashed border-white/30 rounded-2xl cursor-pointer bg-white/10 backdrop-blur-sm hover:bg-white/15 hover:border-white/50 transition ${pastedText ? 'opacity-50 pointer-events-none' : ''}`}>
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <svg className="w-10 h-10 mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="mb-1 text-sm text-gray-300">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-400 mb-2">
                        TXT, DOCX, PDF (max 10MB)
                      </p>
                      {uploadedFile && (
                        <div className="mt-4 px-4 py-2 bg-white/20 rounded-lg flex items-center gap-2">
                          <p className="text-white text-sm font-medium">
                            📄 {uploadedFile.name}
                          </p>
                          <button
                            onClick={(e) => {
                              e.preventDefault()
                              handleClearFile()
                            }}
                            className="text-white hover:text-red-400 transition ml-2 cursor-pointer border border-white/20 rounded-2xl px-2 py-1"
                          >
                            Remove
                          </button>
                        </div>
                      )}
                    </div>
                    <input type="file" className="hidden" accept=".txt,.docx,.pdf" onChange={handleFileChange} disabled={!!pastedText} />
                  </label>
                </div>
              </div>
              <div className="flex justify-center mt-4">
                <button
                  onClick={handleSummarize}
                  disabled={loading}
                  className="px-12 py-3 bg-white hover:bg-gray-100 text-black font-bold text-base rounded-2xl transition transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Analyzing...' : 'Summarize Now'}
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="mb-8 animate-fade-in">
                <button
                  onClick={handleBackToInput}
                  className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white font-medium text-sm rounded-2xl transition-all duration-300 border border-white/20 hover:scale-105 hover:shadow-lg"
                >
                  ← Back to Input
                </button>
              </div>
              <div className="space-y-8">
                <div
                  id="topic"
                  className="bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl p-8 scroll-mt-24 animate-slide-in-left hover:bg-white/15 hover:border-purple-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/20"
                  style={{ animationDelay: '0.1s' }}
                >
                  <Topic data={topicData} />
                </div>
                <div
                  id="sentiment"
                  className="bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl p-8 scroll-mt-24 animate-slide-in-right hover:bg-white/15 hover:border-blue-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/20"
                  style={{ animationDelay: '0.2s' }}
                >
                  <Sentiment data={sentimentData} />
                </div>
                <div
                  id="summary"
                  className="bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl p-8 scroll-mt-24 animate-slide-in-left hover:bg-white/15 hover:border-teal-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-teal-500/20"
                  style={{ animationDelay: '0.3s' }}
                >
                  <Summary data={summaryData} />
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}

export default App
