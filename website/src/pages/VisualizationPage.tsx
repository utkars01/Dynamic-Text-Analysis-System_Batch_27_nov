import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { BarChart3, ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageLayout from "@/components/PageLayout";
import useTextStore from "@/store/textStore";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
  Legend,
} from "recharts";

const VisualizationPage = () => {
  const navigate = useNavigate();
  const { originalText, keywords, topicModel, sentiment } = useTextStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!originalText) {
      navigate("/input");
      return;
    }

    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, [originalText, navigate]);

  const topKeywords = keywords.slice(0, 15);
  
  const colors = [
    "hsl(252, 85%, 60%)",
    "hsl(280, 70%, 55%)",
    "hsl(350, 85%, 65%)",
    "hsl(252, 85%, 70%)",
    "hsl(280, 70%, 65%)",
  ];

  return (
    <PageLayout>
      <div className="container mx-auto px-6 py-16">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent to-accent/70 flex items-center justify-center mx-auto mb-6">
              <BarChart3 className="w-8 h-8 text-accent-foreground" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Visual Insights
            </h1>
            <p className="text-lg text-muted-foreground">
              Explore patterns and trends in your content
            </p>
          </motion.div>

          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-10 h-10 text-primary animate-spin" />
            </div>
          ) : (
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Word Cloud */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="rounded-2xl bg-card border border-border shadow-medium p-6"
              >
                <h2 className="text-xl font-semibold text-foreground mb-6">Word Cloud</h2>
                <div className="min-h-[300px] flex flex-wrap items-center justify-center gap-3 p-4">
                  {keywords.slice(0, 25).map((keyword, index) => {
                    const size = Math.max(0.8, Math.min(2.5, keyword.count / 3));
                    const colorIndex = index % colors.length;
                    return (
                      <motion.span
                        key={keyword.word}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3, delay: index * 0.02 }}
                        style={{
                          fontSize: `${size}rem`,
                          color: colors[colorIndex],
                        }}
                        className="font-semibold hover:scale-110 transition-transform cursor-default"
                      >
                        {keyword.word}
                      </motion.span>
                    );
                  })}
                </div>
              </motion.div>

              {/* Bar Chart */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="rounded-2xl bg-card border border-border shadow-medium p-6"
              >
                <h2 className="text-xl font-semibold text-foreground mb-6">Keyword Frequency</h2>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={topKeywords.slice(0, 10)}
                      layout="vertical"
                      margin={{ top: 0, right: 20, bottom: 0, left: 60 }}
                    >
                      <XAxis type="number" axisLine={false} tickLine={false} />
                      <YAxis
                        type="category"
                        dataKey="word"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "hsl(var(--card))",
                          border: "1px solid hsl(var(--border))",
                          borderRadius: "0.75rem",
                          boxShadow: "var(--shadow-md)",
                        }}
                        labelStyle={{ color: "hsl(var(--foreground))" }}
                      />
                      <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                        {topKeywords.slice(0, 10).map((_, index) => (
                          <Cell key={index} fill={colors[index % colors.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>

              {/* Topic Distribution */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="lg:col-span-2 rounded-2xl bg-card border border-border shadow-medium p-6"
              >
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-6">
                  <div>
                    <h2 className="text-xl font-semibold text-foreground">Topic Distribution</h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      Dominant topic:{" "}
                      <span className="font-medium text-foreground">{topicModel.dominantTopic ?? "—"}</span>
                      {" "}• Sentiment:{" "}
                      <span className="font-medium text-foreground">{sentiment.label ?? "—"}</span>
                    </p>
                  </div>
                  {topicModel.dominantTopicKeyTerms.length > 0 && (
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium text-foreground">Key terms:</span>{" "}
                      {topicModel.dominantTopicKeyTerms.slice(0, 6).join(", ")}
                    </div>
                  )}
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                  {/* Pie chart */}
                  <div className="h-[320px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={topicModel.distribution}
                          dataKey="score"
                          nameKey="topic"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={3}
                        >
                          {topicModel.distribution.map((_, index) => (
                            <Cell key={index} fill={colors[index % colors.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          formatter={(value: number) => `${Math.round(value * 100)}%`}
                          contentStyle={{
                            backgroundColor: "hsl(var(--card))",
                            border: "1px solid hsl(var(--border))",
                            borderRadius: "0.75rem",
                            boxShadow: "var(--shadow-md)",
                          }}
                          labelStyle={{ color: "hsl(var(--foreground))" }}
                        />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Topic vs Sentiment (simple bar proxy) */}
                  <div className="h-[320px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={topicModel.topicVsSentiment} margin={{ top: 0, right: 20, bottom: 0, left: 10 }}>
                        <XAxis dataKey="topic" tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                        <YAxis axisLine={false} tickLine={false} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "hsl(var(--card))",
                            border: "1px solid hsl(var(--border))",
                            borderRadius: "0.75rem",
                            boxShadow: "var(--shadow-md)",
                          }}
                          labelStyle={{ color: "hsl(var(--foreground))" }}
                        />
                        <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                          {topicModel.topicVsSentiment.map((_, index) => (
                            <Cell key={index} fill={colors[index % colors.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                    <p className="text-xs text-muted-foreground mt-3">
                      Demo note: this chart uses topic distribution weights combined with the overall sentiment label.
                      It’s a simple visualization for presentations (not a full statistical model).
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>
          )}

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="mt-10 flex justify-center"
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

export default VisualizationPage;
