import { useState, useCallback, useRef } from 'react';
import api from '../api/client';
import type { AnalysisResult, AnalysisStage } from '../types';

const STAGE_DELAYS: [AnalysisStage, number][] = [
  ['uploading', 600],
  ['extracting', 1200],
  ['analyzing_skills', 1000],
  ['scoring', 1500],
  ['matching', 2000],
  ['generating', 0], // stays until API returns
];

export function useAnalysis() {
  const [stage, setStage] = useState<AnalysisStage>('idle');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef(false);

  const analyze = useCallback(async (file: File, keywords?: string) => {
    abortRef.current = false;
    setError(null);
    setResult(null);

    // Start perceived-speed animation
    const stagePromise = (async () => {
      for (const [s, delay] of STAGE_DELAYS) {
        if (abortRef.current) return;
        setStage(s);
        if (delay > 0) await new Promise((r) => setTimeout(r, delay));
      }
    })();

    // Actual API call in parallel
    const apiPromise = (async (): Promise<AnalysisResult> => {
      const formData = new FormData();
      formData.append('file', file);
      const params = keywords ? `?target_keywords=${encodeURIComponent(keywords)}` : '';
      const res = await api.post(`/analyze-resume${params}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
      });
      return res.data;
    })();

    try {
      const [, data] = await Promise.all([stagePromise, apiPromise]);
      abortRef.current = true;

      // Ensure interview_questions and rewrite_suggestions have defaults
      if (!data.interview_questions) {
        data.interview_questions = { behavioral: [], technical: [], situational: [], role_based: [], total: 0 };
      }
      if (!data.rewrite_suggestions) {
        data.rewrite_suggestions = { rewritten_sections: {}, improvements_count: 0, score_boost_estimate: 0, keyword_insertions: [], summary_suggestion: null, tips: [] };
      }

      setResult(data);
      setStage('complete');
    } catch (err: any) {
      abortRef.current = true;
      const msg = err?.response?.data?.detail || err?.message || 'Analysis failed';
      setError(msg);
      setStage('error');
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current = true;
    setStage('idle');
    setResult(null);
    setError(null);
  }, []);

  return { stage, result, error, analyze, reset };
}
