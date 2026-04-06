import apiClient from "./apiClient";
import { PredictionPoint, MonthlyPM25 } from "../types/prediction";

const predictionService = {
  getShortTerm: async (): Promise<PredictionPoint[]> => {
    const response = await apiClient.get("predictions/short-term");
    return response.data;
  },
  
  getMonthly: async (): Promise<MonthlyPM25[]> => {
    const response = await apiClient.get("predictions/monthly");
    return response.data;
  },

  computeInteractive: async (city: string, features: Record<string, number>) => {
    try {
      console.log(`[AI Lab] Computing for ${city}...`, features);
      const response = await apiClient.post("predictions/compute", { city, features });
      return response.data;
    } catch (err) {
      console.error("[AI Lab] Computation failed:", err);
      throw err;
    }
  }
};

export default predictionService;
