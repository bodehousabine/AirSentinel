"use client";

import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import authService from "@/services/authService";
import userService from "@/services/userService";
import { Mail, Lock, Eye, EyeOff, ArrowLeft, Image as ImageIcon, User, Loader2 } from "lucide-react";
import { notify } from "@/utils/toast";

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [city, setCity] = useState("Douala");
  const [avatar, setAvatar] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    if (password !== confirmPassword) {
      notify.error("Les mots de passe ne correspondent pas.");
      setIsLoading(false);
      return;
    }

    try {
      // 1. Inscription + Connexion (récupère le token direct)
      await authService.register({
        email,
        full_name: fullName,
        password,
        subscribed_city: city
      });

      notify.success("Compte créé avec succès ! Bienvenue.");

      // 2. Upload de l'avatar si présent
      if (avatar) {
        const loadingToast = notify.loading("Envoi de votre photo de profil...");
        try {
          await userService.uploadAvatar(avatar);
          notify.dismiss(loadingToast);
          notify.success("Photo de profil mise à jour.");
        } catch (avatarErr: any) {
          notify.dismiss(loadingToast);
          console.error("Erreur lors de l'upload de l'avatar:", avatarErr);
          const detail = avatarErr.response?.data?.detail || "Vérifiez vos paramètres Supabase.";
          notify.error(`Profil prêt, mais l'image a échoué : ${detail}`);
        }
      }

      // 3. Redirection vers la carte
      router.push('/dashboard/carte');
    } catch (err: any) {
      console.error("Erreur d'inscription:", err);
      const detail = err.response?.data?.detail || "Une erreur est survenue lors de l'inscription.";
      notify.error(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 sm:p-6 bg-[url('/joel1.jpg')] bg-cover bg-center bg-no-repeat overflow-hidden">
      {/* Dark gradient overlay to ensure text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#020c18]/80 via-[#020c18]/60 to-[#020c18]/90 backdrop-blur-[2px]"></div>

      <div className="relative z-10 w-full max-w-[400px] animate-fade-up my-8">
        {/* Main Glass Card */}
        <div className="glass-card w-full pt-8 pb-16 sm:pb-24 px-5 sm:px-8 flex flex-col items-center relative overflow-hidden">

          {/* Back Button */}
          <Link href="/" className="absolute top-6 left-6 text-gray-400 hover:text-white transition-colors z-30">
            <ArrowLeft className="w-6 h-6" />
          </Link>

          {/* Logo - completely inside the card so nothing overflows */}
          <div className="relative w-[100px] h-[100px] mb-4 drop-shadow-[0_0_15px_rgba(0,212,177,0.5)] animate-float flex-shrink-0">
            <Image
              src="/LogoAir.png"
              alt="AirSentinel Logo"
              fill
              className="object-contain"
              priority
            />
          </div>

          {/* Header Text */}
          <div className="text-center w-full mb-6">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              AirSentinel Cameroun
            </h1>
            <p className="text-sm text-gray-300 mt-1">
              L'IA au Service d'un Air Plus Pur
            </p>
          </div>

          <h2 className="text-[1.35rem] font-medium text-white mb-6">
            Créer un compte
          </h2>

          <form className="w-full flex flex-col gap-5 sm:gap-6" onSubmit={handleRegister}>

            {/* Profile Image Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">Image de profil</label>
              <div className="relative group">
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setAvatar(e.target.files?.[0] || null)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[3.5rem] file:mr-4 file:h-full file:px-3 file:border-0 file:text-[11px] file:font-semibold file:bg-[var(--teal)] file:text-[#020c18] hover:file:bg-[#00b396] text-white text-sm focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all cursor-pointer overflow-hidden flex items-center"
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[var(--teal)]">
                  <ImageIcon className="w-5 h-5 opacity-90 group-focus-within:opacity-100 transition-opacity" />
                </div>
              </div>
            </div>

            {/* Full Name Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">Nom Complet</label>
              <div className="relative group">
                <input
                  type="text"
                  placeholder="Jean Dupont"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[3.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all"
                  required
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[var(--teal)]">
                  <User className="w-5 h-5 opacity-90 group-focus-within:opacity-100 transition-opacity" />
                </div>
              </div>
            </div>

            {/* Email Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">Email</label>
              <div className="relative group">
                <input
                  type="email"
                  autoComplete="email"
                  placeholder="votre@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[3.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all"
                  required
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[var(--teal)]">
                  <Mail className="w-5 h-5 opacity-90 group-focus-within:opacity-100 transition-opacity" />
                </div>
              </div>
            </div>

            {/* City Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">Ville de résidence</label>
              <div className="relative group">
                <select
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[3.5rem] text-white text-sm focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all appearance-none cursor-pointer"
                  required
                >
                  {["Douala", "Yaoundé", "Garoua", "Maroua", "Bafoussam", "Bamenda", "Kribi", "Bertoua", "Ebolowa", "Ngaoundéré", "Buéa"].map((c) => (
                    <option key={c} value={c} className="bg-[#020c18] text-white">
                      {c}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[var(--teal)]">
                  <User className="w-5 h-5 opacity-90 group-focus-within:opacity-100 transition-opacity" />
                </div>
                {/* Custom arrow for the select */}
                <div className="absolute inset-y-0 right-10 flex items-center pointer-events-none">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Password Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">Password</label>
              <div className="relative group">
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="Mot de passe"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[5.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all mb-1"
                  required
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center gap-2">
                  <Lock className="w-5 h-5 text-[var(--teal)] opacity-90 group-focus-within:opacity-100 transition-opacity pointer-events-none" />
                  <div
                    className="flex items-center text-gray-400 hover:text-white cursor-pointer transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                  </div>
                </div>
              </div>
            </div>

            {/* Confirm Password Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">Confirmation du mot de passe</label>
              <div className="relative group">
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="Confirmez le mot de passe"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[5.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all"
                  required
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center gap-2">
                  <Lock className="w-5 h-5 text-[var(--teal)] opacity-90 group-focus-within:opacity-100 transition-opacity pointer-events-none" />
                  <div
                    className="flex items-center text-gray-400 hover:text-white cursor-pointer transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                  </div>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full mt-4 !font-medium flex items-center justify-center gap-2 disabled:opacity-70"
            >
              {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
              {isLoading ? "Création du compte..." : "Créer mon compte"}
            </button>
          </form>

          {/* Footer Text */}
          <div className="mt-20 text-[15px] text-gray-300 text-center">
            Déjà un compte?{" "}
            <Link href="/login" className="text-white hover:text-[var(--teal)] font-medium transition-colors">
              Connectez-vous
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
