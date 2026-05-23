export type Role = 'patient' | 'provider' | 'admin' | 'volunteer' | 'family';

export interface User {
  user_id: number;
  username: string;
  full_name: string;
  role: Role;
}

export interface TherapySession {
  session_id: number;
  patient_name: string;
  therapist_name: string;
  session_date: string;
  notes: string;
  status: 'scheduled' | 'completed' | 'cancelled';
}

export interface FollowUpRecord {
  record_id: number;
  patient_id?: number;
  patient_name?: string;
  record_type: 'injection' | 'medication' | 'checkup';
  description: string;
  due_date: string;
  status: 'pending' | 'completed' | 'overdue';
}

export interface Article {
  article_id: number;
  title: string;
  body: string;
  topic: string;
  author_name: string;
  created_at: string;
}

export interface SupportResource {
  _id: string;
  name: string;
  category: 'peer' | 'counselor' | 'hotline';
  contact: string;
  description: string;
}

export interface JournalEntry {
  _id: string;
  content: string;
  mood: 'great' | 'good' | 'okay' | 'low' | 'struggling';
  created_at: string;
}

export interface Exercise {
  _id: string;
  name: string;
  stage: string;
  description: string;
  duration_min: number;
}

export interface Reminder {
  type: 'therapy' | 'overdue';
  message: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface AdminStats {
  users: number;
  therapy_sessions: number;
  followup_records: number;
  articles: number;
  journals: number;
  exercises: number;
  support_resources: number;
}
