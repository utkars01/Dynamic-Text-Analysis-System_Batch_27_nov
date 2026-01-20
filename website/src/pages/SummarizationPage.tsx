import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { FileText, Download, Loader2, ChevronDown, ChevronUp, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageLayout from "@/components/PageLayout";
import useTextStore from "@/store/textStore";
import { analyzeForDemo } from "@/lib/nlpDemo";

const SummarizationPage = () => {
  const navigate = useNavigate();
  const { originalText, summary, setSummary, keywords, setSentiment, setTopicModel, setDatasetSummary, topicModel } =
    useTextStore();
  const [isLoading, setIsLoading] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);

  useEffect(() => {
    if (!originalText) {
      navigate("/input");
      return;
    }

    if (!summary) {
      generateSummary();
    }
  }, [originalText, summary, navigate]);

  const generateSummary = async () => {
    setIsLoading(true);
    
    // Simulate API call to backend
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    // Extractive summarization: score sentences by keyword importance, then select top ones
    const sentences = originalText.split(/[.!?]+/).filter((s) => s.trim().length > 20);
    
    // Build keyword frequency map for scoring
    const keywordMap = new Map<string, number>();
    keywords.forEach((k) => keywordMap.set(k.word.toLowerCase(), k.count));
    
    // Score each sentence by summing keyword frequencies
    const scoredSentences = sentences.map((sentence) => {
      const words = sentence.toLowerCase().match(/\b[a-z]{4,}\b/g) || [];
      const score = words.reduce((sum, word) => sum + (keywordMap.get(word) || 0), 0);
      return { sentence: sentence.trim(), score };
    });
    
    // Sort by score and take top sentences (aim for ~30% of original, but at least 2-3 sentences)
    const topSentences = scoredSentences
      .sort((a, b) => b.score - a.score)
      .slice(0, Math.max(2, Math.min(5, Math.ceil(sentences.length * 0.3))))
      .map((s) => s.sentence);
    
    // Create summary: if we have good sentences, use them; otherwise fallback to first few
    let summaryText: string;
    if (topSentences.length > 0 && topSentences[0].length > 0) {
      summaryText = topSentences.join(". ") + ".";
    } else {
      // Fallback: use first few sentences
      summaryText = sentences.slice(0, Math.min(3, sentences.length)).join(". ") + ".";
    }
    
    setSummary(summaryText);

    // Also compute sentiment/topics once, so other pages already have data.
    // This keeps the demo smooth (student-friendly, no extra backend).
    const analysis = await analyzeForDemo({ text: originalText, keywords });
    setDatasetSummary(analysis.datasetSummary);
    setSentiment(analysis.sentiment.label, analysis.sentiment.score);
    setTopicModel(analysis.topicModel);

    setIsLoading(false);
  };

  const downloadSummary = () => {
    if (!summary) return;
    
    const blob = new Blob([summary], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "narrative-nexus-summary.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <PageLayout>
      <div className="container mx-auto px-6 py-16">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center mx-auto mb-6 shadow-glow">
              <FileText className="w-8 h-8 text-primary-foreground" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Text Summary
            </h1>
            <p className="text-lg text-muted-foreground">
              A concise, rewritten summary of your content
            </p>
          </motion.div>

          {/* Summary Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="rounded-2xl bg-card border border-border shadow-medium overflow-hidden"
          >
            {isLoading ? (
              <div className="p-12 text-center">
                <Loader2 className="w-10 h-10 text-primary animate-spin mx-auto mb-4" />
                <p className="text-muted-foreground">Generating summary...</p>
              </div>
            ) : (
              <div className="p-8">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 rounded-full bg-primary" />
                  <span className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                    Summary
                  </span>
                </div>
                <p className="text-lg text-foreground leading-relaxed">{summary}</p>
              </div>
            )}
          </motion.div>

          {/* Original Text Collapsible */}
          {!isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-6"
            >
              <button
                onClick={() => setShowOriginal(!showOriginal)}
                className="w-full flex items-center justify-between p-4 rounded-xl bg-secondary/50 hover:bg-secondary transition-colors"
              >
                <span className="text-sm font-medium text-muted-foreground">
                  View Original Text
                </span>
                {showOriginal ? (
                  <ChevronUp className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                )}
              </button>
              
              {showOriginal && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-3 p-6 rounded-xl bg-muted/50 border border-border max-h-60 overflow-y-auto"
                >
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {originalText}
                  </p>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* Topic + distribution quick view */}
          {!isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.25 }}
              className="mt-6 rounded-2xl bg-card border border-border p-5"
            >
              <p className="text-sm font-medium text-muted-foreground mb-1">Dominant topic</p>
              <p className="text-base text-foreground mb-2">
                {topicModel.dominantTopic ?? "Topic will appear here after analysis."}
              </p>
              {topicModel.distribution.length > 0 && (
                <p className="text-xs text-muted-foreground">
                  Topics detected:{" "}
                  {topicModel.distribution
                    .slice(0, 6)
                    .map((t) => t.topic)
                    .join(", ")}
                  {topicModel.distribution.length > 6 ? " ..." : ""}
                </p>
              )}
            </motion.div>
          )}

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button
              variant="default"
              size="lg"
              onClick={downloadSummary}
              disabled={!summary}
            >
              <Download className="w-5 h-5" />
              Download Summary
            </Button>
            <Button variant="outline" size="lg" onClick={() => navigate("/dashboard")}>
              <ArrowLeft className="w-5 h-5" />
              Back to Dashboard
            </Button>
          </motion.div>
        </div>
      </div>
    </PageLayout>
  );
};

export default SummarizationPage;
