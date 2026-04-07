import apiClient from "./apiClient";
import { KPIResponse, AlerteHistorique } from "../types/pollution";

const kpiService = {
  getNationalKPIs: async (city?: string): Promise<KPIResponse> => {
    const url = city ? `kpis?city=${encodeURIComponent(city)}` : "kpis";
    const response = await apiClient.get(url);
    return response.data;
  },

  getAlertesHistorique: async (): Promise<AlerteHistorique[]> => {
    const response = await apiClient.get("alertes");
    return response.data;
  }
};

export default kpiService;
