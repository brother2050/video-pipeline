import { create } from "zustand";
import type { ProjectResponse } from "@/types";

interface ProjectState {
  currentProject: ProjectResponse | null;
  setCurrentProject: (project: ProjectResponse | null) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  currentProject: null,
  setCurrentProject: (project) => set({ currentProject: project }),
}));
