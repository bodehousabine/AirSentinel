"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import authService from "../services/authService";
import { User as UserType } from "../types/auth";
import { User, Home, LogOut, Loader2 } from "lucide-react";
import { notify } from "@/utils/toast";

export default function Navbar() {
  const [currentUser, setCurrentUser] = useState<UserType | null>(null);
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
          <span>Accueil</span>
        </Link>

        {isLoading ? (
          <Loader2 className="w-5 h-5 text-[var(--teal)] animate-spin" />
        ) : currentUser ? (
          <div className="flex items-center gap-3 pl-4 border-l border-white/10">
            <div className="max-sm:hidden text-right">
              <p className="text-[13px] font-medium text-white leading-tight">
                {currentUser.full_name || "Utilisateur"}
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
              
              {/* Simple logout tooltip/button on hover or click */}
              <button 
                onClick={handleLogout}
                className="absolute top-12 right-0 bg-slate-900 border border-white/10 px-3 py-2 rounded-lg text-xs text-rose-400 flex items-center gap-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap hover:bg-rose-500/10"
              >
                <LogOut size={14} />
                Déconnexion
              </button>
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
