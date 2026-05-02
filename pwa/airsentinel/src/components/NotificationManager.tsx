"use client";

import { useEffect } from "react";
import { getMessaging, getToken, onMessage } from "firebase/messaging";
import app from "@/lib/firebase";
import apiClient from "@/services/apiClient";
import authService from "@/services/authService";
import toast from "react-hot-toast";

export default function NotificationManager() {
  useEffect(() => {
    const setupNotifications = async () => {
      // 1. Vérifier si l'utilisateur est connecté
      if (!authService.isAuthenticated()) return;

      try {
        // 2. Demander la permission
        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
          console.log("Permission de notification refusée.");
          return;
        }

        // 3. Récupérer le token FCM
        const messaging = getMessaging(app);
        
        // Note: Remplacez par votre vraie clé VAPID si possible
        const token = await getToken(messaging, {
          vapidKey: "BCOhvQLvI5jxno6kfSATjGtotNS-ratoHpGgG0O7lTfmHP_utjn1a2CbgGjOEmmN6o6ZgwfhU0wRtceWfbQ95Lg"
        });

        if (token) {
          console.log("Token FCM récupéré:", token);
          // 4. Envoyer au backend
          await apiClient.post("/notifications/update-token", { fcm_token: token });
        }

        // 5. Écouter les messages quand l'app est au premier plan
        onMessage(messaging, (payload) => {
          console.log("Message reçu au premier plan:", payload);
          toast.success(`${payload.notification?.title}: ${payload.notification?.body}`, {
            duration: 5000,
            icon: "🚨",
          });
        });
      } catch (error) {
        console.error("Erreur lors de la configuration des notifications:", error);
      }
    };

    setupNotifications();
  }, []);

  return null; // Ce composant ne rend rien visuellement
}
