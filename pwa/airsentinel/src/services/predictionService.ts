import apiClient from "./apiClient";
import { PredictionPoint, MonthlyPM25 } from "../types/prediction";

const predictionService = {
  getShortTerm: async (): Promise<PredictionPoint[]> => {
    const response = await apiClient.get("/predictions/short-term");
    return response.data;
  },
  
  getMonthly: async (): Promise<MonthlyPM25[]> => {
    const response = await apiClient.get("/predictions/monthly");
    return response.data;
  }
};

export default predictionService;
