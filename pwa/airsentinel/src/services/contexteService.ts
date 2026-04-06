import apiClient from "./apiClient";

export interface DonutEntry {
  label: string;
  valeur: number;
  couleur: string;
}

export interface ComparaisonAnnuelle {
  annee_courante: number;
  pm25_an_courant: number;
  annee_precedente: number;
  pm25_an_precedent: number;
  evolution_pct: number;
}

export interface ContexteResponse {
  donut_niveaux: DonutEntry[];
  donut_polluants: DonutEntry[];
  comparaison_annuelle: ComparaisonAnnuelle | null;
  uv_ozone: {
    uv_index: number;
    ozone_ppb: number;
    source: string;
  };
}

const contexteService = {
  getContexte: async (): Promise<ContexteResponse> => {
    const response = await apiClient.get("contexte");
    return response.data;
  }
};

export default contexteService;
