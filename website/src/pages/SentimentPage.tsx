import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Smile, Frown, ArrowLeft, Loader2, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageLayout from "@/components/PageLayout";
import useTextStore from "@/store/textStore";
import { analyzeForDemo } from "@/lib/nlpDemo";

const SentimentPage = () => {
  const navigate = useNavigate();
  const { originalText, sentiment, setSentiment, keywords, setTopicModel, setDatasetSummary, topicModel } = useTextStore();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!originalText) {
      navigate("/input");
      return;
    }

    if (!sentiment.label) {
      analyzeSentiment();
    }
  }, [originalText, sentiment, navigate]);

  const analyzeSentiment = async () => {
    setIsLoading(true);

    // Use the same demo analysis as the rest of the app.
    // This reads `public/models/demo_outputs.json` if present (precomputed from /models),
    // and falls back to a tiny heuristic so the UI always works.
    await new Promise((resolve) => setTimeout(resolve, 900));
    const analysis = await analyzeForDemo({ text: originalText, keywords });
    setDatasetSummary(analysis.datasetSummary);
    setSentiment(analysis.sentiment.label, analysis.sentiment.score);
    setTopicModel(analysis.topicModel);

    setIsLoading(false);
  };

  const isPositive = sentiment.label === "Positive";
  // kept for potential future UI tweaks (progress labels etc.)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const scorePercent = sentiment.score !== null ? Math.abs(sentiment.score * 100) : 0;

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
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 ${
              isLoading ? "bg-muted" : isPositive ? "bg-positive shadow-lg" : "bg-negative shadow-lg"
            }`}>
              {isLoading ? (
                <Loader2 className="w-8 h-8 text-muted-foreground animate-spin" />
              ) : isPositive ? (
                <Smile className="w-8 h-8 text-positive-foreground" />
              ) : (
                <Frown className="w-8 h-8 text-negative-foreground" />
              )}
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Sentiment Analysis
            </h1>
            <p className="text-lg text-muted-foreground">
              Understanding the emotional tone of your text
            </p>
          </motion.div>

          {/* Results Card */}
          {isLoading ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl bg-card border border-border shadow-medium p-12 text-center"
            >
              <Loader2 className="w-10 h-10 text-primary animate-spin mx-auto mb-4" />
              <p className="text-muted-foreground">Analyzing sentiment...</p>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className={`rounded-2xl border-2 shadow-medium overflow-hidden ${
                isPositive ? "border-positive/30 bg-positive/5" : "border-negative/30 bg-negative/5"
              }`}
            >
              <div className="p-8 text-center">
                {/* Sentiment Label */}
                <motion.div
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.2 }}
                  className={`inline-flex items-center gap-3 px-6 py-3 rounded-full mb-8 ${
                    isPositive ? "bg-positive/20" : "bg-negative/20"
                  }`}
                >
                  {isPositive ? (
                    <Smile className="w-8 h-8 text-positive" />
                  ) : (
                    <Frown className="w-8 h-8 text-negative" />
                  )}
                  <span className={`text-2xl font-bold ${isPositive ? "text-positive" : "text-negative"}`}>
                    {sentiment.label}
                  </span>
                </motion.div>

                {/* Polarity Score */}
                <div className="mb-8">
                  <p className="text-sm text-muted-foreground mb-3">Polarity Score</p>
                  <p className={`text-5xl font-bold ${isPositive ? "text-positive" : "text-negative"}`}>
                    {sentiment.score?.toFixed(3)}
                  </p>
                </div>

                {/* Score Bar */}
                <div className="max-w-md mx-auto mb-8">
                  <div className="flex justify-between text-xs text-muted-foreground mb-2">
                    <span>Negative</span>
                    <span>Neutral</span>
                    <span>Positive</span>
                  </div>
                  <div className="h-3 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${50 + (sentiment.score || 0) * 50}%` }}
                      transition={{ duration: 0.8, delay: 0.3 }}
                      className={`h-full rounded-full ${isPositive ? "bg-positive" : "bg-negative"}`}
                    />
                  </div>
                </div>

                {/* Explanation */}
                <div className="flex items-start gap-3 p-4 rounded-xl bg-muted/50 text-left max-w-md mx-auto">
                  <Info className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-muted-foreground">
                    This score reflects the overall emotional tone of the text. A score closer to 1 
                    indicates strong positive sentiment, while closer to -1 indicates strong negative sentiment.
                  </p>
                </div>

                {/* Dominant topic inline summary */}
                <div className="mt-6 text-left max-w-md mx-auto">
                  <p className="text-sm font-medium text-muted-foreground mb-1">Dominant topic (from NMF/keywords)</p>
                  <p className="text-base text-foreground">
                    {topicModel.dominantTopic ?? "Topic will appear here after analysis."}
                  </p>
                  {topicModel.dominantTopicKeyTerms.length > 0 && (
                    <p className="mt-2 text-xs text-muted-foreground">
                      Key terms:{" "}
                      <span className="font-medium">
                        {topicModel.dominantTopicKeyTerms.slice(0, 8).join(", ")}
                      </span>
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-8 flex justify-center"
          >
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

export default SentimentPage;
