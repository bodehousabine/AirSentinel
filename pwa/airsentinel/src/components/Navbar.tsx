"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import authService from "../services/authService";
import predictionService from "../services/predictionService";
import { User as UserType } from "../types/auth";
import { User, Home, LogOut, Loader2, Bell, BellOff, Mail, Globe } from "lucide-react";
import { notify } from "@/utils/toast";
import { useLanguage } from "@/context/LanguageContext";
import LanguageSwitcher from "@/components/LanguageSwitcher";

export default function Navbar() {
  const { t, lang, setLang } = useLanguage();
  const [currentUser, setCurrentUser] = useState<UserType | null>(null);
  const [originalCity, setOriginalCity] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchUser = async () => {
      if (authService.isAuthenticated()) {
        try {
          const user = await authService.getCurrentUser();
          setCurrentUser(user);
        } catch (err) {
          console.error("Échec de récupération de l'utilisateur:", err);
        }
      }
      setIsLoading(false);
    };
    fetchUser();
  }, []);

  const handleLogout = () => {
    authService.logout();
    notify.success("Déconnexion réussie.");
    router.push("/login");
  };

  const handleToggleAlerts = async () => {
    if (!currentUser) {
      console.log("[Navbar] Pas d'utilisateur connecté.");
      return;
    }
    
    const targetCity = currentUser.subscribed_city;
    const currentEnabled = currentUser.is_alerts_enabled;
    
    if (!targetCity) {
      notify.error("Veuillez d'abord choisir une ville dans votre profil.");
      router.push("/dashboard/profil");
      return;
    }

    try {
      const loading = notify.loading(currentEnabled ? "Désactivation..." : `Activation des alertes...`);
      
      await predictionService.subscribeToCityAlerts(targetCity, !currentEnabled);
      
      // Mettre à jour l'état local
      const updatedUser = { ...currentUser, is_alerts_enabled: !currentEnabled };
      setCurrentUser(updatedUser);
      
      notify.dismiss(loading);
      notify.success(!currentEnabled ? `Alertes activées sur ${targetCity} !` : "Alertes désactivées.");
    } catch (err) {
      console.error("[Navbar] Erreur toggle alertes:", err);
      notify.error("Impossible de modifier vos alertes.");
    }
  };

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-[100] px-4 sm:px-8 h-16 flex items-center justify-between border-b border-white/5 bg-[#020c18]/80 backdrop-blur-xl"
    >
      <div className="flex items-center gap-2.5">
        <Image src="/LogoAir.png" alt="AirSentinel Logo" width={34} height={34} className="drop-shadow-[0_0_10px_rgba(0,212,177,0.3)]" />
        <span className="text-lg font-bold text-white tracking-tight">
          Air<span className="text-[var(--teal)]">Sentinel</span>
        </span>
      </div>

      <div className="flex items-center gap-4 sm:gap-6">
        <Link href="/" className="max-sm:hidden flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors">
          <Home size={16} />
          <span>{t('nav_home')}</span>
        </Link>

        <LanguageSwitcher />

        {currentUser && (
          <button
            onClick={handleToggleAlerts}
            className={`
              relative flex items-center gap-2 px-3 h-9 rounded-full border transition-all duration-300 group
              ${currentUser.is_alerts_enabled 
                ? "bg-[var(--teal)]/10 border-[var(--teal)]/40 text-[var(--teal)] shadow-[0_0_15px_rgba(0,212,177,0.2)]" 
                : "bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20"}
            `}
            title={currentUser.is_alerts_enabled ? `${t('nav_alerts_active')} (${currentUser.subscribed_city})` : "Activer les alertes"}
          >
            {currentUser.is_alerts_enabled ? (
              <>
                <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-[var(--teal)] rounded-full animate-pulse shadow-[0_0_8px_rgba(0,212,177,0.8)]" />
                <Bell size={16} className="animate-wiggle" />
                <span className="text-[11px] font-bold tracking-wider max-sm:hidden uppercase">{t('nav_alerts_active')}</span>
              </>
            ) : (
              <>
                <BellOff size={16} />
                <span className="text-[11px] font-medium max-sm:hidden">{t('nav_alerts_off')}</span>
              </>
            )}
          </button>
        )}

        {isLoading ? (
          <Loader2 className="w-5 h-5 text-[var(--teal)] animate-spin" />
        ) : currentUser ? (
          <div className="flex items-center gap-3 pl-4 border-l border-white/10">
            <div className="max-sm:hidden text-right">
              <p className="text-[13px] font-medium text-white leading-tight">
                {currentUser.full_name || t('nav_user_placeholder')}
              </p>
            </div>
            
            <div className="relative group">
              <div className="w-9 h-9 rounded-full border-2 border-[var(--teal)]/30 overflow-hidden bg-slate-800 flex items-center justify-center cursor-pointer group-hover:border-[var(--teal)] transition-all">
                {currentUser.avatar_url ? (
                  <Image 
                    src={currentUser.avatar_url} 
                    alt={currentUser.full_name || "User"} 
                    fill 
                    className="object-cover"
                  />
                ) : (
                  <User size={18} className="text-[var(--teal)]" />
                )}
              </div>
              
              {/* Profile Dropdown */}
              <div className="absolute top-12 right-0 bg-slate-900 border border-white/10 p-1.5 rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap min-w-[160px] backdrop-blur-2xl">
                <Link 
                  href="/dashboard/profil"
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] text-gray-300 hover:bg-white/5 hover:text-white transition-all mb-1"
                >
                  <User size={14} className="text-[var(--teal)]" />
                  Mon Profil
                </Link>
                <button 
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] text-rose-400 hover:bg-rose-500/10 transition-all"
                >
                  <LogOut size={14} />
                  {t('nav_logout')}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <Link 
            href="/login" 
            className="w-9 h-9 rounded-full bg-[var(--teal)]/10 border border-[var(--teal)]/20 flex items-center justify-center text-[var(--teal)] hover:bg-[var(--teal)]/20 transition-all"
          >
            <User size={18} />
          </Link>
        )}
      </div>
    </nav>
  );
}
