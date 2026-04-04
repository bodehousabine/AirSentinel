import apiClient from "./apiClient";
import { KPIResponse, AlerteHistorique } from "../types/pollution";

const kpiService = {
  getNationalKPIs: async (): Promise<KPIResponse> => {
    const response = await apiClient.get("/kpis");
    return response.data;
  },

  getAlertesHistorique: async (): Promise<AlerteHistorique[]> => {
    const response = await apiClient.get("/alertes");
    return response.data;
  }
};

export default kpiService;
