"use client";

import { HeartPulse, ShieldCheck, UserPlus, Info, Zap } from "lucide-react";

const RECOMMENDATIONS = [
  { id: 1, title: "Masques FFP2", desc: "Recommandé pour les déplacements en zone urbaine dense.", color: "#00d4b1" },
  { id: 2, title: "Hydratation", desc: "Buvez au moins 2.5L d'eau pour aider à l'élimination des toxines.", color: "#0ea5e9" },
  { id: 3, title: "Activités physiques", desc: "Évitez les efforts intenses en extérieur entre 10h et 16h.", color: "#f59e0b" },
];

export default function SantePage() {
  return (
    <main className="p-6 pb-24 max-w-4xl mx-auto">
      <header className="mb-10">
        <h1 className="text-3xl font-extrabold text-[#e0f2fe] mb-2 tracking-tight flex items-center gap-3">
          Santé & Bien-être <HeartPulse className="text-[#ef4444]" size={28} />
        </h1>
        <p className="text-[#e0f2fe]/50 text-sm">Simulateur IRS et conseils de protection personnalisés.</p>
      </header>

      {/* IRS Simulator Card */}
      <div className="glass-card mb-10 overflow-hidden relative border-[#ef4444]/30 shadow-[#ef4444]/5">
        <div className="p-10 flex flex-col items-center text-center">
          <div className="w-24 h-24 rounded-full border-4 border-[#ef4444]/20 flex items-center justify-center relative mb-6">
            <div className="text-4xl font-black text-[#ef4444]">78</div>
            <div className="absolute inset-0 rounded-full border-4 border-[#ef4444] border-t-transparent animate-spin-slow"></div>
          </div>
          <h3 className="text-xl font-bold mb-1 italic">Indice IRS Actuel</h3>
          <p className="text-xs font-black uppercase tracking-widest text-[#ef4444] mb-8 bg-[#ef4444]/10 px-4 py-1.5 rounded-full inline-block">
            Niveau élevé
          </p>
          <button className="w-full sm:w-auto px-8 py-3 bg-[#ef4444] text-white rounded-xl font-bold shadow-2xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2 justify-center">
            <Zap size={18} fill="currentColor" /> Simuler un profil vulnérable
          </button>
        </div>
      </div>

      {/* Recommendations Section */}
      <h4 className="text-xs font-black text-[#e0f2fe]/40 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
        <ShieldCheck size={14} /> Préconisations de sécurité
      </h4>

      <div className="flex flex-col gap-4">
        {RECOMMENDATIONS.map((rec) => (
          <div key={rec.id} className="glass-card p-6 flex items-start gap-5 hover:border-white/20 transition-colors">
            <div 
              className="w-1.5 h-full absolute left-0 top-0 rounded-l-full" 
              style={{ backgroundColor: rec.color }}
            />
            <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center shrink-0">
              <Info size={18} className="opacity-50" />
            </div>
            <div>
              <h5 className="font-bold text-lg mb-1 tracking-tight">{rec.title}</h5>
              <p className="text-sm text-[#e0f2fe]/60 leading-relaxed italic">{rec.desc}</p>
            </div>
          </div>
        ))}

        <button className="flex items-center justify-center gap-3 w-full py-4 glass-card border-dashed border-white/10 text-[#e0f2fe]/40 hover:text-[#e0f2fe]/80 transition-all text-sm font-medium mt-4">
          <UserPlus size={18} /> Ajouter un profil familial (Enfant, Asthme...)
        </button>
      </div>
    </main>
  );
}
