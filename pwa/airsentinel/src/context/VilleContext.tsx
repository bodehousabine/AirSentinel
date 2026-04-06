"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface VilleContextType {
  ville: string | null;
  setVille: (ville: string | null) => void;
  selectVille: (ville: string) => void;
}

const VilleContext = createContext<VilleContextType | undefined>(undefined);

export function VilleProvider({ children }: { children: ReactNode }) {
  const [ville, setVille] = useState<string | null>(null);

  const selectVille = (newVille: string) => {
    setVille(newVille);
  };

  return (
    <VilleContext.Provider value={{ ville, setVille, selectVille }}>
      {children}
    </VilleContext.Provider>
  );
}

export function useVille() {
  const context = useContext(VilleContext);
  if (!context) {
    throw new Error("useVille must be used within a VilleProvider");
  }
  return context;
}
