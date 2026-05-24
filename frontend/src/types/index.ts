// ──────────────────────────────────────────────
// ResuMatch AI — TypeScript Interfaces
// ──────────────────────────────────────────────

export interface ContactInfo {
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  website: string | null;
  has_email: boolean;
  has_phone: boolean;
  has_linkedin: boolean;
}

export interface Skill {
  name: string;
  category: string;
  proficiency: 'expert' | 'advanced' | 'intermediate' | 'beginner' | 'unknown';
  years: number | null;
  demand: number;
}

export interface ScoreBreakdownItem {
  score: number;
  weight: number;
  weighted: number;
  details: string[];
}

export interface ATSScore {
  total_score: number;
  grade: string;
  breakdown: {
    parsing: ScoreBreakdownItem;
    keywords: ScoreBreakdownItem;
    formatting: ScoreBreakdownItem;
    structure: ScoreBreakdownItem;
  };
  recommendations: string[];
}

export interface CareerPath {
  title: string;
  from_role: string;
  match_percentage: number;
  skills_have: string[];
  skills_missing: string[];
  timeline: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  description: string;
  tags: string[];
  location: string;
  salary_min: number | null;
  salary_max: number | null;
  url: string;
  source: string;
  posted_at: string;
  company_logo: string;
  match_score?: number;
}

export interface ResumeInfo {
  page_count: number;
  word_count: number;
  contact_info: ContactInfo;
  sections_found: string[];
}

// Interview Questions
export interface InterviewQuestion {
  question: string;
  skill?: string;
  tip?: string;
  category?: string;
  context?: string;
}

export interface InterviewQuestions {
  behavioral: InterviewQuestion[];
  technical: InterviewQuestion[];
  situational: InterviewQuestion[];
  role_based: InterviewQuestion[];
  total: number;
}

// Resume Rewriter
export interface RewrittenBullet {
  original: string;
  rewritten: string;
  changes: string[];
  keywords_added: string[];
  improved: boolean;
}

export interface RewriteSuggestions {
  rewritten_sections: Record<string, RewrittenBullet[]>;
  improvements_count: number;
  score_boost_estimate: number;
  keyword_insertions: { keyword: string; inserted_in: string }[];
  summary_suggestion: string | null;
  tips: string[];
}

export interface AnalysisResult {
  success: boolean;
  elapsed_seconds: number;
  resume: ResumeInfo;
  ats_score: ATSScore;
  skills: {
    skills: Skill[];
    total_years: number | null;
    skill_locations: Record<string, string[]>;
  };
  career_paths: CareerPath[];
  matched_jobs: Job[];
  interview_questions: InterviewQuestions;
  rewrite_suggestions: RewriteSuggestions;
}

export type AnalysisStage =
  | 'idle'
  | 'uploading'
  | 'extracting'
  | 'analyzing_skills'
  | 'scoring'
  | 'matching'
  | 'generating'
  | 'complete'
  | 'error';

// Auth
export interface User {
  id: number;
  email: string;
  name: string;
  role: 'user' | 'admin';
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

// Admin
export interface AdminUser {
  id: number;
  email: string;
  name: string;
  role: string;
  created_at: string;
  last_login: string | null;
  is_active: number;
}

export interface Session {
  id: number;
  login_at: string;
  logout_at: string | null;
  ip_address: string;
  user_agent: string;
  email: string;
  name: string;
  role: string;
}

export interface AdminStats {
  total_users: number;
  active_today: number;
  total_analyses: number;
  total_sessions: number;
  avg_ats_score: number;
  system: {
    process_memory_mb: number;
    system_total_mb?: number;
    system_available_mb?: number;
    system_percent_used?: number;
  };
}
