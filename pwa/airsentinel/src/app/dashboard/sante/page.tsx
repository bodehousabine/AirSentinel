"use client";

import { useEffect, useState } from "react";
import { HeartPulse, ShieldCheck, Loader2, Wind, Activity, MapPin, ChevronDown } from "lucide-react";
import healthService, { ProfilRecommandation } from "@/services/healthService";
import mapService from "@/services/mapService";
import { useVille } from "@/context/VilleContext";
import { VillePoint } from "@/types/map";

export default function SantePage() {
  const [recommendations, setRecommendations] = useState<ProfilRecommandation[]>([]);
  const [loading, setLoading] = useState(true);
  const [villes, setVilles] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const { ville, selectVille } = useVille();

  useEffect(() => {
    const fetchVilles = async () => {
      try {
        const points = await mapService.getMapPoints();
        const sortedVilles = points.map(p => p.city).sort((a, b) => a.localeCompare(b, 'fr'));
        setVilles(sortedVilles);
      } catch (err) {
        console.error("Erreur chargement villes:", err);
      }
    };
    fetchVilles();
  }, []);

  useEffect(() => {
    if (!ville) {
      setLoading(false);
      return;
    }

    const fetchHealthData = async () => {
      setLoading(true);
      try {
        const data = await healthService.getRealRecommendations(ville);
        setRecommendations(data);
      } catch (err) {
        console.error("Erreur chargement santé:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHealthData();
  }, [ville]);

  const handleSelectVille = (villeChoisie: string) => {
    selectVille(villeChoisie);
    setShowDropdown(false);
  };

  if (!ville) {
    return (
      <main className="p-6 pb-24 max-w-5xl mx-auto animate-in fade-in duration-700">
        <header className="mb-10">
          <h1 className="text-4xl font-black text-[#e0f2fe] mb-2 tracking-tight flex items-center gap-3">
            Santé & <span className="text-[#ef4444]">Protection</span> <HeartPulse className="text-[#ef4444]" size={32} />
          </h1>
          <p className="text-[#e0f2fe]/50 text-sm font-medium italic">Préconisations IA personnalisées selon la qualité de l&apos;air détectée.</p>
        </header>

        <div className="glass-card p-10 flex flex-col items-center justify-center min-h-[400px]">
          <div className="w-20 h-20 rounded-full bg-[#00d4b1]/10 flex items-center justify-center mb-6">
            <MapPin className="text-[#00d4b1]" size={40} />
          </div>
          <h2 className="text-2xl font-black text-white mb-4 text-center">Choisissez votre ville</h2>
          <p className="text-gray-400 text-center mb-8 max-w-md">
            Sélectionnez une ville pour obtenir des recommandations personnalisées selon la qualité de l'air local.
          </p>

          <div className="relative w-full max-w-md">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="w-full flex items-center justify-between px-6 py-4 bg-[#020c18] border border-white/10 rounded-2xl text-white hover:border-[#00d4b1]/50 transition-colors"
            >
              <span className="font-medium">Sélectionner une ville...</span>
              <ChevronDown className={`text-gray-400 transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
            </button>

            {showDropdown && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-[#020c18] border border-white/10 rounded-2xl shadow-2xl overflow-hidden max-h-[300px] overflow-y-auto z-50">
                {villes.map((v) => (
                  <button
                    key={v}
                    onClick={() => handleSelectVille(v)}
                    className="w-full text-left px-6 py-3 hover:bg-[#00d4b1]/10 text-white font-medium transition-colors"
                  >
                    {v}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-12 p-6 bg-blue-500/5 rounded-3xl border border-blue-500/10 flex items-center gap-6">
          <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400 shrink-0">
            <span className="text-xl font-bold">i</span>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed font-medium">
            <b>Note IA :</b> Ces recommandations sont basées sur les normes de l&apos;OMS. Si vous ressentez des difficultés respiratoires persistantes, contactez immédiatement les services de santé de votre district.
          </p>
        </div>

        <div className="h-[120px] sm:hidden" />
      </main>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#ef4444] animate-spin" />
      </div>
    );
  }

  const globalRisk = recommendations[0]?.niveau_risque || "MODÉRÉ";
  const globalColor = recommendations[0]?.couleur || "#FFC107";

  return (
    <main className="p-6 pb-24 max-w-5xl mx-auto animate-in fade-in duration-700">
      <header className="mb-10">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-black text-[#e0f2fe] mb-2 tracking-tight flex items-center gap-3">
              Santé & <span className="text-[#ef4444]">Protection</span> <HeartPulse className="text-[#ef4444]" size={32} />
            </h1>
            <p className="text-[#00d4b1] text-sm font-bold mb-2 flex items-center gap-2">
              <MapPin size={14} /> Données pour : {ville}
            </p>
            <p className="text-[#e0f2fe]/50 text-sm font-medium italic">Préconisations IA personnalisées selon la qualité de l&apos;air détectée.</p>
          </div>
          <button
            onClick={() => selectVille("")}
            className="px-4 py-2 bg-[#00d4b1] text-white font-bold rounded-xl shadow-lg hover:bg-[#00b89c] hover:scale-105 transition-all active:scale-95 flex items-center gap-2 shrink-0"
          >
            <MapPin size={14} />
            Changer
          </button>
        </div>
      </header>

      <div className="glass-card mb-6 overflow-hidden relative border-[#ef4444]/20 shadow-2xl">
        <div className="absolute top-0 left-0 w-full h-1" style={{ backgroundColor: globalColor }} />
        <div className="p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-6 md:gap-8">
           <div className="flex flex-col items-center md:items-start text-center md:text-left">
              <h3 className="text-2xl font-black text-white italic tracking-tight mb-2">État Sanitaire Actuel</h3>
              <div className="flex items-center gap-3 px-6 py-2 rounded-full border border-white/5 bg-white/5">
                 <div className="w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: globalColor, boxShadow: `0 0 12px ${globalColor}` }} />
                 <span className="text-sm font-black uppercase tracking-[0.2em]" style={{ color: globalColor }}>
                   Niveau {globalRisk}
                 </span>
              </div>
           </div>
           
           <div className="grid grid-cols-2 gap-4 w-full md:w-auto">
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5 text-center">
                 <Wind className="text-blue-400 mx-auto mb-2" size={20} />
                 <div className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Ventilation</div>
                 <div className="text-sm font-bold text-white">{globalRisk === 'FAIBLE' ? 'Optimale' : 'Limitée'}</div>
              </div>
              <div className="p-4 bg-white/5 rounded-2xl border border-white/5 text-center">
                 <Activity className="text-[#ef4444] mx-auto mb-2" size={20} />
                 <div className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Effort Sportif</div>
                 <div className="text-sm font-bold text-white">{globalRisk === 'FAIBLE' ? 'Conseillé' : 'Prudence'}</div>
              </div>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {recommendations.map((rec, idx) => (
          <div key={idx} className="glass-card p-6 flex flex-col gap-6 group hover:border-white/20 transition-all duration-500 border-white/5">
            <div className="flex items-center justify-between">
               <div className="flex items-center gap-4">
                  <div className="text-3xl p-3 bg-white/5 rounded-2xl group-hover:scale-110 transition-transform">{rec.icone}</div>
                  <h5 className="font-black text-xl text-white tracking-tight">{rec.profil}</h5>
               </div>
               <div className="w-3 h-3 rounded-full" style={{ backgroundColor: rec.couleur }} />
            </div>
            
            <div>
               <p className="text-sm text-[#e0f2fe]/70 leading-relaxed font-medium italic mb-6">
                  &quot;{rec.message}&quot;
               </p>
               <div className="space-y-3">
                  <h6 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Actions Correctives :</h6>
                  {rec.actions.map((action, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 bg-white/5 rounded-xl border border-white/5 text-xs font-bold text-gray-300 group-hover:bg-white/10 transition-colors">
                       <ShieldCheck className="text-[#00d4b1] shrink-0" size={16} />
                       {action}
                    </div>
                  ))}
               </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-12 p-6 bg-blue-500/5 rounded-3xl border border-blue-500/10 flex items-center gap-6">
         <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400 shrink-0">
            <span className="text-xl font-bold">i</span>
         </div>
         <p className="text-xs text-gray-400 leading-relaxed font-medium">
            <b>Note IA :</b> Ces recommandations sont basées sur les normes de l&apos;OMS. Si vous ressentez des difficultés respiratoires persistantes, contactez immédiatement les services de santé de votre district.
         </p>
      </div>

      <div className="h-[120px] sm:hidden" />
    </main>
  );
}
