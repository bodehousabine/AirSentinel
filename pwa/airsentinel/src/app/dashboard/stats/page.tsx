"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { BarChart2, TrendingUp, Activity, MapPin, Loader2, Award, Zap } from "lucide-react";
import Image from "next/image";
import kpiService from "@/services/kpiService";
import mapService from "@/services/mapService";
import { KPIResponse } from "@/types/pollution";

export default function StatsPage() {
  const [kpis, setKpis] = useState<KPIResponse | null>(null);
  const [analyses, setAnalyses] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpiData, analysesData] = await Promise.all([
          kpiService.getNationalKPIs(),
          mapService.getMapAnalyses()
        ]);
        setKpis(kpiData);
        setAnalyses(analysesData);
      } catch (err) {
        console.error("Erreur chargement stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Transformer les données pour le graphique
  const chartData = analyses?.pm25_par_region ? 
    Object.entries(analyses.pm25_par_region).map(([name, value]) => ({
      name,
      value
    })).sort((a, b) => (b.value as number) - (a.value as number)) : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#00d4b1] animate-spin" />
      </div>
    );
  }

  return (
    <main className="relative min-h-screen overflow-x-hidden">
      <div className="fixed inset-0 -z-10">
        <Image
          src="/stat.jpg"
          alt="Statistiques Background"
          fill
          className="object-cover opacity-20 scale-105"
          priority
        />
        <div className="absolute inset-0 bg-[#020617]/90 backdrop-blur-[2px]" />
      </div>

      <div className="p-6 pb-32 max-w-6xl mx-auto relative z-10">
        <header className="mb-12 animate-in fade-in slide-in-from-left duration-700">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-1 w-8 bg-[#00d4b1] rounded-full shadow-[0_0_10px_rgba(0,212,177,0.5)]" />
            <span className="text-[10px] font-black tracking-[0.3em] text-[#00d4b1] uppercase">AirSentinel Insights Live</span>
          </div>
          <h1 className="text-5xl font-black text-white mb-3 tracking-tighter leading-none">
            Analyse des <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00d4b1] to-[#0ea5e9]">Données Nationales</span>
          </h1>
          <p className="text-gray-400 text-sm font-medium max-w-md antialiased">
            Données agrégées en temps réel depuis {kpis?.total_observations || 0} observations à travers le pays.
          </p>
        </header>

        {/* Top KPIs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard 
            icon={<Activity />} 
            label="PM2.5 Moyen" 
            value={kpis?.pm25_moyen || 0} 
            unit="µg/m³" 
            color="#00d4b1" 
          />
          <StatCard 
            icon={<TrendingUp />} 
            label="Villes > OMS" 
            value={kpis?.villes_depassant_oms || 0} 
            unit="Villes" 
            color="#ef4444" 
          />
          <StatCard 
            icon={<Zap />} 
            label="Polluant Majeur" 
            value={kpis?.polluant_dominant || "PM2.5"} 
            unit="Type" 
            color="#f59e0b" 
            isText
          />
          <StatCard 
            icon={<MapPin />} 
            label="Points Actifs" 
            value={kpis?.total_observations || 0} 
            unit="Mesures" 
            color="#0ea5e9" 
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Chart */}
          <div className="lg:col-span-2 glass-card p-8 border-white/5 relative overflow-hidden group">
             <div className="flex justify-between items-start mb-10">
                <div>
                   <h3 className="text-xl font-bold text-white tracking-tight">Pollution par Région</h3>
                   <p className="text-xs text-gray-500 font-medium">Répartition géographique de la moyenne PM2.5</p>
                </div>
                <Award className="text-[#00d4b1]/20 group-hover:text-[#00d4b1]/40 transition-colors" size={32} />
             </div>

             <div className="h-[350px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                   <BarChart data={chartData} margin={{ top: 20, right: 10, left: -20, bottom: 40 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                      <XAxis 
                         dataKey="name" 
                         stroke="rgba(255,255,255,0.3)" 
                         fontSize={10} 
                         tickLine={false} 
                         axisLine={false}
                         angle={-45}
                         textAnchor="end"
                      />
                      <YAxis stroke="rgba(255,255,255,0.3)" fontSize={10} tickLine={false} axisLine={false} />
                      <Tooltip 
                         cursor={{ fill: 'rgba(0,212,177,0.05)' }}
                         contentStyle={{ 
                            backgroundColor: '#0f172a', 
                            border: '1px solid rgba(255,255,255,0.1)', 
                            borderRadius: '16px',
                            color: '#fff',
                            fontSize: '12px'
                         }}
                      />
                      <Bar 
                        dataKey="value" 
                        radius={[4, 4, 0, 0]} 
                        animationDuration={1500}
                        animationBegin={300}
                      >
                         {chartData.map((entry, index) => (
                           <Cell 
                             key={`cell-${index}`} 
                             fill={index < 3 ? '#00d4b1' : '#1e293b'} 
                             fillOpacity={0.8}
                           />
                         ))}
                      </Bar>
                   </BarChart>
                </ResponsiveContainer>
             </div>
          </div>

          {/* Top Cities Table */}
          <div className="glass-card p-8 border-white/5 border-l-4 border-l-[#ef4444]/50">
             <h3 className="text-xl font-bold text-white mb-6 tracking-tight">Top 5 Villes Critiques</h3>
             <div className="space-y-4">
                {analyses?.top_5_villes_critiques?.map((city: any, idx: number) => (
                   <div key={city.city} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 group hover:bg-white/10 hover:border-[#ef4444]/20 transition-all duration-300">
                      <div className="flex items-center gap-4">
                         <span className="text-lg font-black text-[#ef4444]/40 group-hover:text-[#ef4444] transition-colors">{idx + 1}</span>
                         <span className="text-sm font-bold text-gray-200">{city.city}</span>
                      </div>
                      <div className="flex flex-col items-end">
                         <span className="text-sm font-black text-white">{city.pm25_moyen}</span>
                         <span className="text-[8px] font-black text-[#ef4444] uppercase tracking-widest">µg/m³</span>
                      </div>
                   </div>
                )) || (
                   <p className="text-center text-gray-500 py-10 italic">Aucune donnée critique disponible.</p>
                )}
             </div>
             
             <div className="mt-8 p-4 bg-[#ef4444]/5 rounded-2xl border border-[#ef4444]/10">
                <div className="flex items-center gap-3 mb-2">
                   <AlertCircle className="text-[#ef4444]" size={18} />
                   <span className="text-xs font-black text-[#ef4444] uppercase tracking-widest">Alerte Santé</span>
                </div>
                <p className="text-[10px] text-gray-400 font-medium leading-relaxed">
                   Ces villes présentent des moyennes supérieures à 25 µg/m³. Des actions de prévention sont recommandées.
                </p>
             </div>
          </div>
        </div>
      </div>
    </main>
  );
}

import { AlertCircle } from "lucide-react";

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
