import { writable } from "svelte/store";

function createEditModeStore() {
  const { subscribe, set } = writable(false);
  return {
    subscribe,
    in: () => set(true),
    out: () => set(false),
  };
}

export const editMode = createEditModeStore();
