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
      const response = await apiClient.post("predictions/compute", { city, features });
      return response.data;
    } catch (err: any) {
      console.error("[AI Lab] Computation failed:", err);
      throw err;
    }
  },

  subscribeToCityAlerts: async (city: string) => {
    try {
      const response = await apiClient.put("users/me/subscription", { subscribed_city: city });
      return response.data;
    } catch (err: any) {
      console.error("[Alerts] Subscription failed:", err.message);
      throw err;
    }
  }
};

export default predictionService;
