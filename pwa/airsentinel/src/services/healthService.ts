import apiClient from "./apiClient";

export interface ProfilRecommandation {
  profil: string;
  icone: string;
  niveau_risque: string;
  couleur: string;
  message: string;
  actions: string[];
}

const healthService = {
  getRealRecommendations: async (): Promise<ProfilRecommandation[]> => {
    const response = await apiClient.get("/decision/real");
    return response.data;
  }
};

export default healthService;
