import type { SingleTime } from ".";
import type { Step } from "../config/const";

export interface Application {
  uid: string;
  created_at: string;
  updated_at: string;
  grade: string;
  institute: string;
  major: string;
  rank: string;
  group: string;
  intro: string;
  is_quick: boolean;
  is_project_c?: boolean;
  referrer: string;
  resume: string;
  abandoned: boolean;
  rejected: boolean;
  step: Step;
  candidate_id: string;
  recruitment_id: string;
  interview_allocations_group: SingleTime;
  interview_allocations_team: SingleTime;
  user_detail: null;
  interview_selections: SingleTime[];
  comments: null;
}

export type EditableInfo = Pick<
  Application,
  | "grade"
  | "institute"
  | "major"
  | "rank"
  | "group"
  | "intro"
  | "referrer"
  | "is_quick"
  | "is_project_c"
>;

export type NecessaryInfo = Omit<EditableInfo, "referrer">;

export type Step = keyof typeof Step;
