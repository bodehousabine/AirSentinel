import apiClient from "./apiClient";
import { VillePoint, CarteAnalyses } from "../types/map";

const mapService = {
  /**
   * Récupère la liste des points géolocalisés (villes) pour la carte.
   */
  async getMapPoints(): Promise<VillePoint[]> {
    const response = await apiClient.get<VillePoint[]>("/carte");
    return response.data;
  },

  /**
   * Récupère les analyses globales enrichies pour la carte et le dashboard.
   */
  async getMapAnalyses(): Promise<CarteAnalyses> {
    const response = await apiClient.get<CarteAnalyses>("/carte/analyses");
    return response.data;
  }
};

export default mapService;
