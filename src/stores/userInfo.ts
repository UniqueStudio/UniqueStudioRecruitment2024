import { writable } from "svelte/store";
import type { User } from "../types/user";
import type { EditableInfo } from "../types/application";
import { produce } from "immer";

const createUserStore = () => {
  const { set, subscribe, update } = writable<User>();
  const setInfo = (info: User) => {
    set(info);
  };
  const updateInfo = (newInfo: Omit<EditableInfo, "groups">) => // update all application which have the same recruitment_id with applications[0]
    update((prevInfo) =>
      produce<User>(prevInfo, (draft) => {
        Object.keys(newInfo).forEach((key) => {
          //ly: why group enum in backend can't be same with group enum in frontend?????WTF
          // key === "groups"
          //   ? (draft.applications[0][key] = newInfo[key].map((item: string) => item.toLowerCase()))
          //   : (draft.applications[0][key] = newInfo[key]);
          draft.applications.forEach((_, ia) => {
            if (draft.applications[ia].recruitment_id === draft.applications[0]?.recruitment_id) {
              draft.applications[ia][key] = newInfo[key];
            }
          });
        });
      })
    );

  return {
    subscribe,
    setInfo,
    updateInfo,
  };
};

export const userInfo = createUserStore();
