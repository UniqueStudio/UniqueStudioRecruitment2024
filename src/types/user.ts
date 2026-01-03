import type { Application } from "./application";

//ly: its easy to write type with ChatGPT :)
export interface User {
	uid: string;
	phone: string;
	email: string;
	qq_account?: string;
	name: string;
	avatar_url: string;
	gender: number;
	join_time: string;
	groups: null;
	lark_union_id: string;
	applications: Application[];
}
