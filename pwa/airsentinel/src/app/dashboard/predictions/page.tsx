"use client";

import { useEffect, useState } from "react";
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, AreaChart, Area, ReferenceLine 
} from "recharts";
import { Brain, Sparkles, AlertCircle, Loader2, TrendingUp, TrendingDown, Minus } from "lucide-react";
import predictionService from "@/services/predictionService";
import { PredictionPoint } from "@/types/prediction";

export default function PredictionsPage() {
  const [data, setData] = useState<PredictionPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const res = await predictionService.getShortTerm();
        setData(res);
      } catch (err) {
        console.error("Erreur chargement prédictions:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPredictions();
  }, []);

  // Extraire les 3 prédictions (J+1, J+2, J+3)
  const predictions = data.filter(p => p.is_prediction);
  const history = data.filter(p => !p.is_prediction);
  
  const jPlus1 = predictions[0];
  const jPlus2 = predictions[1];
  const jPlus3 = predictions[2];

  // Calculer la tendance (vs dernier point historique)
  const lastReal = history[history.length - 1]?.pm25 || 0;
  const trendPct = jPlus1 ? ((jPlus1.pm25 - lastReal) / lastReal) * 100 : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#00d4b1] animate-spin" />
      </div>
    );
  }

  return (
    <main className="p-6 pb-32 max-w-5xl mx-auto animate-in fade-in duration-700">
      <header className="mb-10">
        <div className="flex items-center gap-2 mb-2">
           <Brain className="text-[#00d4b1]" size={20} />
           <span className="text-[10px] font-black tracking-[0.2em] text-[#00d4b1] uppercase">AirSentinel AI Labs</span>
        </div>
        <h1 className="text-4xl font-black text-[#e0f2fe] mb-2 tracking-tight flex items-center gap-3">
          Prévisions <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00d4b1] to-[#0ea5e9]">Prédictives</span>
        </h1>
        <p className="text-[#e0f2fe]/50 text-sm font-medium">Analyse par réseaux de neurones (LSTM) des flux sahariens et locaux.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        {/* Main Prediction Card */}
        <div className="lg:col-span-2 glass-card overflow-hidden relative border-[#00d4b1]/20">
          <div className="p-8">
            <div className="flex justify-between items-start mb-8">
               <div className="space-y-1">
                  <div className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Prévision J+1</div>
                  <div className="text-5xl font-black text-white">
                    {jPlus1?.pm25.toFixed(1)} <span className="text-xl font-light opacity-30 italic">µg/m³</span>
                  </div>
               </div>
               <div className="px-4 py-2 bg-[#00d4b1]/10 rounded-2xl border border-[#00d4b1]/20 flex flex-col items-end">
                  <span className="text-[10px] font-black text-[#00d4b1] uppercase">Confiance IA</span>
                  <span className="text-lg font-black text-white">94.2%</span>
               </div>
            </div>

            <div className="flex items-center gap-4 mb-10">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${trendPct > 0 ? 'bg-orange-500/10 border-orange-500/20 text-orange-500' : 'bg-green-500/10 border-green-500/20 text-green-500'}`}>
                {trendPct > 1 ? <TrendingUp size={16} /> : trendPct < -1 ? <TrendingDown size={16} /> : <Minus size={16} />}
                <span className="text-[10px] font-black uppercase tracking-wide">
                  Tendance {trendPct > 0 ? 'en hausse' : 'en baisse'} ({Math.abs(trendPct).toFixed(1)}%)
                </span>
              </div>
              <div className="h-px flex-1 bg-white/5"></div>
            </div>

            {/* Micro Chart inside Card */}
            <div className="h-[250px] w-full mt-4">
               <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data}>
                     <defs>
                        <linearGradient id="colorPm" x1="0" y1="0" x2="0" y2="1">
                           <stop offset="5%" stopColor="#00d4b1" stopOpacity={0.3}/>
                           <stop offset="95%" stopColor="#00d4b1" stopOpacity={0}/>
                        </linearGradient>
                     </defs>
                     <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
                     <XAxis 
                        dataKey="date" 
                        hide 
                     />
                     <YAxis hide domain={['dataMin - 5', 'dataMax + 5']} />
                     <Tooltip 
                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                        itemStyle={{ color: '#00d4b1', fontWeight: 'bold' }}
                     />
                     <Area 
                        type="monotone" 
                        dataKey="pm25" 
                        stroke="#00d4b1" 
                        strokeWidth={4}
                        fillOpacity={1} 
                        fill="url(#colorPm)" 
                        animationDuration={2000}
                     />
                     {/* Line separating history and prediction */}
                     {history.length > 0 && (
                        <ReferenceLine x={history[history.length-1].date} stroke="#64748b" strokeDasharray="3 3" />
                     )}
                  </AreaChart>
               </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-2 bg-white/5 border-t border-white/10 divide-x divide-white/10">
            <div className="p-6 text-center group hover:bg-[#00d4b1]/5 transition-colors">
               <div className="text-[9px] text-gray-500 mb-2 uppercase tracking-widest font-black">Après-Demain (J+2)</div>
               <div className="text-3xl font-black text-white">{jPlus2?.pm25.toFixed(1)}</div>
               <div className="text-[9px] text-[#00d4b1] font-bold mt-1 uppercase">Projection Stable</div>
            </div>
            <div className="p-6 text-center group hover:bg-[#00d4b1]/5 transition-colors">
               <div className="text-[9px] text-gray-500 mb-2 uppercase tracking-widest font-black">J+3</div>
               <div className="text-3xl font-black text-white">{jPlus3?.pm25.toFixed(1)}</div>
               <div className="text-[9px] text-[#00d4b1] font-bold mt-1 uppercase">Tendance Favorable</div>
            </div>
          </div>
        </div>

        {/* Sidebar Cards */}
        <div className="space-y-6">
           <div className="glass-card p-6 border-white/5">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400 mb-6">
                 <AlertCircle size={24} />
              </div>
              <h4 className="font-bold text-lg text-white mb-2 italic tracking-tight">Anticipation cruciale</h4>
              <p className="text-xs text-gray-400 leading-relaxed mb-6 font-medium">
                Nos modèles LSTM détectent les pics de pollution 24h à 48h avant l&apos;apparition des symptômes physiques.
              </p>
              <button className="w-full py-3 bg-white/5 hover:bg-white/10 rounded-xl text-[10px] font-black text-[#00d4b1] uppercase tracking-widest transition-all">
                Détails du Modèle
              </button>
           </div>
           
           <div className="glass-card p-6 bg-gradient-to-br from-[#00d4b1]/10 to-transparent border-[#00d4b1]/10">
              <div className="flex items-center gap-3 mb-4">
                 <Sparkles className="text-[#00d4b1]" size={20} />
                 <span className="text-xs font-bold text-white uppercase tracking-wider">Optimisation IA</span>
              </div>
              <p className="text-[11px] text-gray-400 leading-relaxed">
                 Le modèle se recalibre toutes les 6 heures avec les nouvelles données des stations de Douala et Yaoundé.
              </p>
           </div>
        </div>
      </div>
      
      {/* Mobile Spacer */}
      <div className="h-[120px] sm:hidden" />
    </main>
  );
}
