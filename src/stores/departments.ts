import { writable } from "svelte/store";

export type Departments = Record<string, string[]>;

function createDepartmentsStore() {
	const { set, subscribe } = writable<Departments>({});
	const setDepartments = (data: Departments) => {
		set(data);
	};
	return {
		subscribe,
		setDepartments
	};
}

export const departments = createDepartmentsStore();
