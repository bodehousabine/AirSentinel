"use client";

import { useEffect, useState } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Cell, PieChart, Pie 
} from "recharts";
import { TrendingUp, Activity, MapPin, Loader2, Award, Zap, PieChart as PieIcon, Layers, AlertCircle } from "lucide-react";
import Image from "next/image";
import kpiService from "@/services/kpiService";
import mapService from "@/services/mapService";
import contexteService from "@/services/contexteService";
import { KPIResponse } from "@/types/pollution";
import { useVille } from "@/context/VilleContext";
import { RefreshCcw, XCircle } from "lucide-react";
import CitySelector from "@/components/CitySelector";

export default function StatsPage() {
  const [kpis, setKpis] = useState<KPIResponse | null>(null);
  const [analyses, setAnalyses] = useState<any>(null);
  const [contexte, setContexte] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { ville, setVille } = useVille();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [kpiData, analysesData, contexteData] = await Promise.all([
          kpiService.getNationalKPIs(ville || undefined),
          mapService.getMapAnalyses(), // Toujours national pour le graphique régions
          contexteService.getContexte(ville || undefined)
        ]);
        setKpis(kpiData);
        setAnalyses(analysesData);
        setContexte(contexteData);
      } catch (err) {
        console.error("Erreur chargement stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [ville]);

  // Transformer les données pour le graphique à barres
  // En mode national : PM2.5 par région
  // En mode ville : PM2.5 par région (filtré sur la région de la ville)
  const isNational = !ville || ville === "CAMEROON";
  const barData = analyses?.pm25_par_region ?
    Object.entries(analyses.pm25_par_region).map(([name, value]) => ({
      name,
      value: value as number
    })).sort((a, b) => b.value - a.value) : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#00d4b1] animate-spin" />
      </div>
    );
  }

  // Si aucune ville n'est sélectionnée (ou sélection délibérée du National)
  // On peut décider de forcer le sélecteur si ville est strictement null ET que 
  // l'utilisateur n'a pas encore "dépassé" l'étape de sélection.
  // Pour rester simple et efficace : si ville est null, on affiche le sélecteur.
  // Si l'utilisateur clique sur "National" dans le sélecteur, on pourrait mettre 
  // une valeur spéciale comme "Cameroon" ou simplement autoriser l'affichage.

  return (
    <main className="relative min-h-screen overflow-x-hidden">
      {/* Background Section */}
      <div className="fixed inset-0 -z-10">
        <Image
          src="/joel3.jpg"
          alt="Statistiques Background"
          fill
          className="object-cover opacity-20 scale-105"
          priority
        />
        <div className="absolute inset-0 bg-[#020617]/90 backdrop-blur-[2px]" />
      </div>

      <div className="p-6 pb-64 max-w-6xl mx-auto relative z-10">
        {!ville ? (
          <div className="py-12">
            <header className="mb-12">
               <h1 className="text-5xl font-black text-white mb-3 tracking-tighter">
                 Statistiques <span className="text-[#00d4b1]">Analytiques</span>
               </h1>
               <p className="text-gray-400 text-sm font-medium">Explorez les données de qualité de l&apos;air par zone géographique.</p>
            </header>
            <CitySelector />
          </div>
        ) : (
          <>
            <header className="mb-12 animate-in fade-in slide-in-from-left duration-700">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-1 w-8 bg-[#00d4b1] rounded-full shadow-[0_0_10px_rgba(0,212,177,0.5)]" />
                  <span className="text-[10px] font-black tracking-[0.3em] text-[#00d4b1] uppercase">
                    {ville === "CAMEROON" ? "Situation Nationale" : `Insights: ${ville}`}
                  </span>
                </div>
                
                <button 
                  onClick={() => setVille(null)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-[10px] font-bold text-gray-300 transition-all active:scale-95 group"
                >
                  <RefreshCcw size={14} className="text-[#00d4b1] group-hover:rotate-180 transition-transform duration-500" />
                  CHANGER DE VILLE
                </button>
              </div>
              
              <h1 className="text-5xl font-black text-white mb-3 tracking-tighter leading-none">
                Analyse des <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00d4b1] to-[#0ea5e9]">Données {ville === "CAMEROON" ? "Nationales" : `à ${ville}`}</span>
              </h1>
              <p className="text-gray-400 text-sm font-medium max-w-md antialiased">
                {ville === "CAMEROON" 
                  ? `Données agrégées en temps réel depuis ${kpis?.total_observations || 0} observations à travers le pays.`
                  : `Données spécifiques à la ville de ${ville} basées sur ${kpis?.total_observations || 0} observations.`
                }
              </p>
            </header>

            {/* Top KPIs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <StatCard icon={<Activity />} label="PM2.5 Moyen" value={kpis?.pm25_moyen || 0} unit="µg/m³" color="#00d4b1" />
              <StatCard icon={<TrendingUp />} label="Villes > OMS" value={kpis?.villes_depassant_oms || 0} unit="Villes" color="#ef4444" />
              <StatCard icon={<Zap />} label="Polluant Majeur" value={kpis?.polluant_dominant || "PM2.5"} unit="Type" color="#f59e0b" isText />
              <StatCard icon={<MapPin />} label="Points Actifs" value={kpis?.total_observations || 0} unit="Mesures" color="#0ea5e9" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* Main Bar Chart */}
              <div className="lg:col-span-2 glass-card p-8 border-white/5 relative overflow-hidden group">
                 <div className="flex justify-between items-start mb-10">
                    <div>
                       <h3 className="text-xl font-bold text-white tracking-tight">Pollution par Région</h3>
                       <p className="text-xs text-gray-500 font-medium">Répartition géographique de la moyenne PM2.5</p>
                    </div>
                    <Award className="text-[#00d4b1]/20 group-hover:text-[#00d4b1]/40 transition-colors" size={32} />
                 </div>

                 <div className="h-[350px] min-h-[350px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                       <BarChart data={barData} margin={{ top: 20, right: 10, left: -20, bottom: 40 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" fontSize={10} angle={-45} textAnchor="end" />
                          <YAxis stroke="rgba(255,255,255,0.3)" fontSize={10} tickLine={false} axisLine={false} />
                          <Tooltip 
                             cursor={{ fill: 'rgba(0,212,177,0.05)' }}
                             contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px' }}
                          />
                          <Bar dataKey="value" radius={[4, 4, 0, 0]} animationDuration={1500}>
                             {barData.map((entry, index) => (
                               <Cell key={`cell-${index}`} fill={index < 3 ? '#00d4b1' : '#1e293b'} fillOpacity={0.8} />
                             ))}
                          </Bar>
                       </BarChart>
                    </ResponsiveContainer>
                 </div>
              </div>

              {/* Top Cities Table */}
              <div className="glass-card p-8 border-white/5 border-l-4 border-l-[#ef4444]/50 flex flex-col">
                 <h3 className="text-xl font-bold text-white mb-6 tracking-tight">Top 5 Villes Critiques</h3>
                 <div className="space-y-4 flex-1 overflow-y-auto pr-2">
                    {analyses?.top_5_villes_critiques?.map((city: any, idx: number) => (
                       <div key={city.city} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 group hover:bg-white/10 transition-all duration-300">
                          <div className="flex items-center gap-4">
                             <span className="text-lg font-black text-[#ef4444]/40 group-hover:text-[#ef4444]">{idx + 1}</span>
                             <span className="text-sm font-bold text-gray-200">{city.city}</span>
                          </div>
                          <div className="flex flex-col items-end">
                             <span className="text-sm font-black text-white">{city.pm25_moyen}</span>
                             <span className="text-[8px] font-black text-[#ef4444] uppercase tracking-widest">µg/m³</span>
                          </div>
                       </div>
                    )) || <p className="text-center text-gray-500 py-10 italic">Aucune donnée disponible.</p>}
                 </div>
                 <div className="mt-8 p-4 bg-[#ef4444]/5 rounded-2xl border border-[#ef4444]/10">
                    <div className="flex items-center gap-3 mb-2">
                       <AlertCircle className="text-[#ef4444]" size={18} />
                       <span className="text-xs font-black text-[#ef4444] uppercase tracking-widest">Alerte Santé</span>
                    </div>
                    <p className="text-[10px] text-gray-400 font-medium leading-relaxed">
                       Villes avec moyennes &gt; 25 µg/m³. Vigilance recommandée.
                    </p>
                 </div>
              </div>
            </div>

            {/* Second Row: Advanced Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
               {/* Metric 1: Niveaux IRS (Stacked Progress) */}
               <div className="glass-card p-8 border-white/5 relative group flex flex-col justify-between">
                  <div className="flex items-center gap-3 mb-6">
                     <Activity className="text-amber-400" size={20} />
                     <h3 className="text-lg font-bold text-white">Répartition des Niveaux</h3>
                  </div>
                  
                  <div className="space-y-6">
                    {/* Stacked Progress Bar */}
                    <div className="w-full h-4 rounded-full overflow-hidden flex bg-white/5 border border-white/10 shadow-inner">
                      {contexte?.donut_niveaux?.map((entry: any, index: number) => (
                         <div 
                           key={index} 
                           style={{ width: `${entry.valeur}%`, backgroundColor: entry.couleur }}
                           className="h-full transition-all duration-1000 hover:brightness-125 hover:scale-y-110 origin-center"
                           title={`${entry.label}: ${entry.valeur}%`}
                         />
                      ))}
                    </div>

                    {/* Labels grid */}
                    <div className="grid grid-cols-2 gap-4">
                      {contexte?.donut_niveaux?.map((entry: any, index: number) => (
                         <div key={index} className="flex justify-between items-center bg-white/5 hover:bg-white/10 transition-colors p-3 rounded-xl border border-white/10">
                           <div className="flex items-center gap-2">
                             <div className="w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.3)]" style={{ backgroundColor: entry.couleur, boxShadow: `0 0 8px ${entry.couleur}` }} />
                             <span className="text-xs font-bold text-gray-300">{entry.label}</span>
                           </div>
                           <span className="text-sm font-black text-white">{entry.valeur}%</span>
                         </div>
                      ))}
                    </div>
                  </div>
               </div>

               {/* Metric 2: Polluants Mix (Horizontal Bars) */}
               <div className="glass-card p-8 border-white/5 relative group">
                  <div className="flex items-center gap-3 mb-6">
                     <Layers className="text-[#00d4b1]" size={20} />
                     <h3 className="text-lg font-bold text-white">Mélange de Polluants</h3>
                  </div>
                  
                  <div className="space-y-5">
                    {contexte?.donut_polluants?.length > 0 ? (
                        contexte.donut_polluants.map((entry: any, index: number) => (
                           <div key={index} className="space-y-2">
                             <div className="flex justify-between items-center">
                               <span className="text-xs font-bold text-gray-300">{entry.label}</span>
                               <span className="text-xs font-black text-white">{entry.valeur}%</span>
                             </div>
                             <div className="w-full h-2 rounded-full overflow-hidden bg-white/5 border border-white/5">
                                <div 
                                  className="h-full rounded-full transition-all duration-1000 relative"
                                  style={{ width: `${entry.valeur}%`, backgroundColor: entry.couleur }}
                                >
                                  <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/30" />
                                </div>
                             </div>
                           </div>
                        ))
                    ) : (
                        <div className="flex items-center justify-center h-full min-h-[150px]">
                           <p className="text-gray-500 italic text-sm">Aucune donnée multi-polluants</p>
                        </div>
                    )}
                  </div>
               </div>
            </div>

            {/* Third Row: Comparison & Enviro */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
               {/* Evolution Card */}
               <div className="glass-card p-8 border-white/5 flex flex-col justify-between overflow-hidden relative">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                     <TrendingUp size={80} />
                  </div>
                  <div>
                     <div className="text-[10px] font-black text-[#00d4b1] uppercase tracking-widest mb-2">Tendance Annuelle</div>
                     <h3 className="text-2xl font-black text-white mb-2">
                        {contexte?.comparaison_annuelle?.evolution_pct > 0 ? '+' : ''}{contexte?.comparaison_annuelle?.evolution_pct}%
                     </h3>
                     <p className="text-xs text-gray-500 font-medium leading-relaxed">
                        Évolution du PM2.5 moyen entre {contexte?.comparaison_annuelle?.annee_precedente} et {contexte?.comparaison_annuelle?.annee_courante}.
                     </p>
                  </div>
                  <div className={`mt-6 inline-flex items-center gap-2 text-[10px] font-black px-3 py-1.5 rounded-full w-fit ${contexte?.comparaison_annuelle?.evolution_pct <= 0 ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                     {contexte?.comparaison_annuelle?.evolution_pct <= 0 ? 'AMÉLIORATION' : 'DÉGRADATION'}
                  </div>
               </div>

               {/* UV Index Card */}
               <div className="glass-card p-8 border-white/5 relative group bg-gradient-to-br from-amber-500/5 to-transparent">
                  <div className="flex items-center justify-between mb-6">
                     <div className="text-[10px] font-black text-amber-500 uppercase tracking-widest">Index UV maximal</div>
                     <Zap className="text-amber-500" size={18} />
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                     <span className="text-4xl font-black text-white">{contexte?.uv_ozone?.uv_index}</span>
                     <span className="text-xs font-bold text-amber-500/50 uppercase">Elevé</span>
                  </div>
                  <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                     <div 
                        className="h-full bg-gradient-to-r from-amber-500 to-orange-600 transition-all duration-1000" 
                        style={{ width: `${(contexte?.uv_ozone?.uv_index / 12) * 100}%` }}
                     />
                  </div>
                  <p className="text-[10px] text-gray-500 mt-4 italic">Source: {contexte?.uv_ozone?.source}</p>
               </div>

               {/* Ozone Card */}
               <div className="glass-card p-8 border-white/5 relative group bg-gradient-to-br from-blue-500/5 to-transparent">
                  <div className="flex items-center justify-between mb-6">
                     <div className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Ozone (O3)</div>
                     <Activity className="text-blue-400" size={18} />
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                     <span className="text-4xl font-black text-white">{contexte?.uv_ozone?.ozone_ppb}</span>
                     <span className="text-xs font-bold text-blue-400/50 uppercase">PPB</span>
                  </div>
                  <p className="text-xs text-gray-400 font-medium leading-relaxed mt-4">
                     Concentration moyenne en surface. Niveau habituel pour la zone équatoriale.
                  </p>
               </div>
            </div>

            <div className="h-[120px] sm:hidden" />
          </>
        )}
      </div>
    </main>
  );
}

function StatCard({ icon, label, value, unit, color, isText }: any) {
  return (
    <div className="glass-card group p-5 flex flex-col gap-4 border-white/5 hover:border-white/10 transition-all duration-500">
      <div 
        className="w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
        style={{ backgroundColor: `${color}15`, color: color }}
      >
        {icon}
      </div>
      <div>
        <div className={`font-black text-white tracking-tight ${isText ? 'text-2xl pt-1' : 'text-3xl'}`}>
          {value}
        </div>
        <div 
           className="text-[9px] font-black uppercase tracking-widest mt-1.5 flex items-center gap-1.5 opacity-80"
           style={{ color: color }}
        >
          {label} <span className="opacity-20">|</span> {unit}
        </div>
      </div>
    </div>
  );
}
