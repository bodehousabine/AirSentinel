import apiClient from "./apiClient";
import { PredictionPoint, MonthlyPM25 } from "../types/prediction";

const predictionService = {
  getShortTerm: async (city?: string | null): Promise<PredictionPoint[]> => {
    // Si la ville n'est pas spécifiée ou est "CAMEROON", on prend Douala par défaut pour les prédictions
    // car le modèle a besoin d'une localisation concrète.
    const targetCity = (!city || city === "CAMEROON") ? "Douala" : city;
    const response = await apiClient.get(`predictions/short-term?city=${encodeURIComponent(targetCity)}`);
    return response.data;
  },

  getMonthly: async (): Promise<MonthlyPM25[]> => {
    const response = await apiClient.get("predictions/monthly");
    return response.data;
  },

  computeInteractive: async (city: string, features: Record<string, number>) => {
    try {
      const targetCity = (city === "CAMEROON") ? "Douala" : city;
      const response = await apiClient.post("predictions/compute", { city: targetCity, features });
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
