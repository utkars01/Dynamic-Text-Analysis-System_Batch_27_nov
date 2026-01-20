import { create } from "zustand";

export type SentimentLabel = "Positive" | "Neutral" | "Negative";

export type TopicDistributionItem = {
  topic: string;
  score: number; // 0..1 normalized
};

export type TopicVsSentimentPoint = {
  topic: string;
  sentiment: SentimentLabel;
  value: number; // simple demo score/count
};

interface TextState {
  originalText: string;
  summary: string | null;
  sentiment: {
    label: SentimentLabel | null;
    score: number | null;
  };
  keywords: { word: string; count: number }[];
  datasetSummary: {
    wordCount: number;
    charCount: number;
    sentenceCount: number;
  } | null;
  topicModel: {
    dominantTopic: string | null;
    dominantTopicKeyTerms: string[];
    distribution: TopicDistributionItem[];
    topicVsSentiment: TopicVsSentimentPoint[];
  };
  isLoading: boolean;
  setOriginalText: (text: string) => void;
  setSummary: (summary: string) => void;
  setSentiment: (label: SentimentLabel, score: number) => void;
  setKeywords: (keywords: { word: string; count: number }[]) => void;
  setDatasetSummary: (summary: NonNullable<TextState["datasetSummary"]>) => void;
  setTopicModel: (topicModel: TextState["topicModel"]) => void;
  setLoading: (loading: boolean) => void;
  reset: () => void;
}

const useTextStore = create<TextState>((set) => ({
  originalText: "",
  summary: null,
  sentiment: {
    label: null,
    score: null,
  },
  keywords: [],
  datasetSummary: null,
  topicModel: {
    dominantTopic: null,
    dominantTopicKeyTerms: [],
    distribution: [],
    topicVsSentiment: [],
  },
  isLoading: false,
  setOriginalText: (text) => set({ originalText: text }),
  setSummary: (summary) => set({ summary }),
  setSentiment: (label, score) => set({ sentiment: { label, score } }),
  setKeywords: (keywords) => set({ keywords }),
  setDatasetSummary: (datasetSummary) => set({ datasetSummary }),
  setTopicModel: (topicModel) => set({ topicModel }),
  setLoading: (loading) => set({ isLoading: loading }),
  reset: () =>
    set({
      originalText: "",
      summary: null,
      sentiment: { label: null, score: null },
      keywords: [],
      datasetSummary: null,
      topicModel: {
        dominantTopic: null,
        dominantTopicKeyTerms: [],
        distribution: [],
        topicVsSentiment: [],
      },
      isLoading: false,
    }),
}));

export default useTextStore;
