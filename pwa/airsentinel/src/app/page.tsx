"use client";
import Image from "next/image";
import Link from "next/link";
import { User, Home, Map as MapIcon, Bell, BrainCircuit, Activity, ShieldAlert, Database, Zap, Boxes, Wind, Cpu, Layers, Globe, Stethoscope, Code } from "lucide-react";
import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";

const geoUrl = "/cameroon-regions.json";

// ── Mini composants ──────────────────────────────────────────────────────────

function Navbar() {
  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        padding: "12px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: "rgba(2,12,24,0.85)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid rgba(0,212,177,0.15)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <Image src="/LogoAir.png" alt="AirSentinel Logo" width={36} height={36} />
        <span
          style={{
            fontSize: "18px",
            fontWeight: 700,
            color: "#e0f2fe",
            letterSpacing: "-0.02em",
          }}
        >
          Air<span style={{ color: "#00d4b1" }}>Sentinel</span>
        </span>
      </div>
      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <a href="#pilliers" style={{ color: "rgba(224,242,254,0.7)", fontSize: "14px", textDecoration: "none" }} className="max-sm:hidden">
          Fonctionnalités
        </a>
        <Link href="/login" style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "36px", height: "36px", borderRadius: "50%", background: "rgba(0,212,177,0.1)", border: "1px solid rgba(0,212,177,0.25)", transition: "all 0.3s" }} onMouseEnter={(e) => e.currentTarget.style.background = "rgba(0,212,177,0.2)"} onMouseLeave={(e) => e.currentTarget.style.background = "rgba(0,212,177,0.1)"}>
          <User size={18} color="#00d4b1" />
        </Link>
      </div>
    </nav>
  );
}

function StatBadge({ value, label }: { value: string; label: string }) {
  return (
    <div
      className="glass-card"
      style={{ padding: "14px 22px", textAlign: "center", minWidth: "110px" }}
    >
      <div style={{ fontSize: "22px", fontWeight: 700, color: "#00d4b1" }}>{value}</div>
      <div style={{ fontSize: "11px", color: "rgba(224,242,254,0.55)", marginTop: "3px", letterSpacing: "0.06em", textTransform: "uppercase" }}>
        {label}
      </div>
    </div>
  );
}

function PillarCard({
  icon,
  title,
  description,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="card-premium p-8 rounded-2xl flex flex-col gap-6 relative overflow-hidden h-full">
      <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--teal)]/5 blur-[60px] pointer-events-none" />
      
      <div className="icon-glow">
        {icon}
      </div>
      
      <div className="space-y-3">
        <h3 className="text-xl font-bold text-[#e0f2fe] tracking-tight">{title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed font-medium">
          {description}
        </p>
      </div>
      
      {children && <div className="mt-2">{children}</div>}
    </div>
  );
}

// Mini graphe IRS simulé
function MiniChart() {
  const points = [15, 22, 18, 30, 25, 35, 28, 42, 38, 45, 40, 50];
  const max = Math.max(...points);
  const w = 300;
  const h = 80;
  const pts = points
    .map((v, i) => `${(i / (points.length - 1)) * w},${h - (v / max) * h}`)
    .join(" ");
  return (
    <div
      className="glass-card"
      style={{ padding: "16px", marginTop: "8px" }}
    >
      <div style={{ fontSize: "12px", color: "rgba(224,242,254,0.5)", marginBottom: "8px" }}>
        Indice IRS — Tendance nationale
      </div>
      <svg width="100%" viewBox={`0 0 ${w} ${h}`} style={{ overflow: "visible" }}>
        <defs>
          <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00d4b1" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#00d4b1" stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon
          points={`0,${h} ${pts} ${w},${h}`}
          fill="url(#grad)"
        />
        <polyline
          points={pts}
          fill="none"
          stroke="#00d4b1"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}

// Carte Cameroun interactive via react-simple-maps
function CameroonMap() {
  const mapData = [
    { name: "Garoua", coordinates: [13.4, 9.3], val: "0.95" },
    { name: "Douala", coordinates: [9.7, 4.05], val: "9.39" },
    { name: "Yaoundé", coordinates: [11.5, 3.8], val: "0.98" },
    { name: "Bafoussam", coordinates: [10.4, 5.48], val: "0.96" }
  ];

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: "420px",
        margin: "0 auto",
      }}
    >
      <div
        style={{
          background: "linear-gradient(135deg, rgba(0,212,177,0.05) 0%, rgba(14,165,233,0.05) 100%)",
          border: "1px solid rgba(0,212,177,0.2)",
          borderRadius: "20px",
          padding: "16px",
          backdropFilter: "blur(10px)",
        }}
      >
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{
            scale: 2200,
            center: [12.5, 7.5] // Centre visuel approximatif du Cameroun
          }}
          style={{ width: "100%", height: "auto", filter: "drop-shadow(0 0 15px rgba(0,212,177,0.2))" }}
        >
          <Geographies geography={geoUrl}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill="rgba(0,212,177,0.15)"
                  stroke="#00d4b1"
                  strokeWidth={0.5}
                  style={{
                    default: { outline: "none" },
                    hover: { fill: "rgba(0,212,177,0.4)", outline: "none", cursor: "pointer", transition: "all 0.3s" },
                    pressed: { outline: "none" },
                  }}
                />
              ))
            }
          </Geographies>
          {mapData.map(({ name, coordinates, val }) => (
            <Marker key={name} coordinates={coordinates as [number, number]}>
              <circle r={6} fill="#0ea5e9" opacity={0.9} />
              <circle r={6} fill="transparent" stroke="#0ea5e9" strokeWidth={2}>
                <animate attributeName="r" values="6;16;6" dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.8;0;0.8" dur="2s" repeatCount="indefinite" />
              </circle>
              <text
                textAnchor="middle"
                y={-12}
                style={{
                  fill: "#e0f2fe",
                  fontSize: "12px",
                  fontWeight: "bold",
                  textShadow: "0px 2px 4px rgba(0,0,0,0.8)",
                  pointerEvents: "none"
                }}
              >
                {val}
              </text>
            </Marker>
          ))}
        </ComposableMap>
        <div style={{ textAlign: "center", marginTop: "12px" }}>
          <span style={{ fontSize: "11px", color: "rgba(224,242,254,0.5)", letterSpacing: "0.1em" }}>
            CARTE RÉELLE · 10 RÉGIONS
          </span>
        </div>
      </div>
    </div>
  );
}

function TechBadge({ name, icon }: { name: string; icon: React.ReactNode }) {
  return (
    <div className="card-premium px-6 py-5 rounded-2xl flex flex-col items-center gap-3 transition-all cursor-default min-w-[120px]">
      <div className="text-[var(--teal)] opacity-80 group-hover:opacity-100 transition-opacity">
        {icon}
      </div>
      <div className="text-[13px] font-bold text-gray-400 uppercase tracking-widest">{name}</div>
    </div>
  );
}

// ── PWA Footer (Mobile Navigation) ───────────────────────────────────────────
function PWAFooter() {
  return (
    <div
      className="sm:hidden"
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        background: "rgba(2,12,24,0.85)",
        backdropFilter: "blur(12px)",
        borderTop: "1px solid rgba(0,212,177,0.15)",
        padding: "12px 24px",
        paddingBottom: "max(12px, env(safe-area-inset-bottom))", // Support iPhone safe area
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <Link href="/" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "4px", color: "#00d4b1", textDecoration: "none", width: "25%" }}>
        <Home size={22} />
        <span style={{ fontSize: "10px", fontWeight: 600 }}>Accueil</span>
      </Link>
      <Link href="/dashboard" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "4px", color: "rgba(224,242,254,0.5)", textDecoration: "none", width: "25%", transition: "color 0.2s" }} onMouseEnter={(e) => e.currentTarget.style.color = "#00d4b1"} onMouseLeave={(e) => e.currentTarget.style.color = "rgba(224,242,254,0.5)"}>
        <MapIcon size={22} />
        <span style={{ fontSize: "10px", fontWeight: 500 }}>Carte</span>
      </Link>
      <Link href="#pilliers" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "4px", color: "rgba(224,242,254,0.5)", textDecoration: "none", width: "25%", transition: "color 0.2s" }} onMouseEnter={(e) => e.currentTarget.style.color = "#00d4b1"} onMouseLeave={(e) => e.currentTarget.style.color = "rgba(224,242,254,0.5)"}>
        <Bell size={22} />
        <span style={{ fontSize: "10px", fontWeight: 500 }}>Alertes</span>
      </Link>
      <Link href="/login" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "4px", color: "rgba(224,242,254,0.5)", textDecoration: "none", width: "25%", transition: "color 0.2s" }} onMouseEnter={(e) => e.currentTarget.style.color = "#00d4b1"} onMouseLeave={(e) => e.currentTarget.style.color = "rgba(224,242,254,0.5)"}>
        <User size={22} />
        <span style={{ fontSize: "10px", fontWeight: 500 }}>Profil</span>
      </Link>
    </div>
  );
}

// ── Page principale ──────────────────────────────────────────────────────────

export default function LandingPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "linear-gradient(160deg, rgba(2, 12, 24, 0.45) 0%, rgba(3, 18, 35, 0.4) 100%), url('/joel1.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
        color: "#e0f2fe",
        fontFamily: "Inter, sans-serif",
        overflowX: "hidden",
      }}
    >
      <Navbar />

      {/* Blobs décoratifs */}
      <div
        aria-hidden
        style={{
          position: "fixed",
          top: "-200px",
          right: "-200px",
          width: "600px",
          height: "600px",
          background: "radial-gradient(circle, rgba(0,212,177,0.12) 0%, transparent 70%)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />
      <div
        aria-hidden
        style={{
          position: "fixed",
          bottom: "-200px",
          left: "-200px",
          width: "500px",
          height: "500px",
          background: "radial-gradient(circle, rgba(14,165,233,0.10) 0%, transparent 70%)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* ── HERO ─────────────────────────────────────────────────────── */}
      <section
        style={{
          position: "relative",
          zIndex: 1,
          paddingTop: "120px",
          paddingBottom: "80px",
          textAlign: "center",
          padding: "120px 24px 80px",
        }}
      >
        {/* Logo */}
        <div className="animate-float" style={{ marginBottom: "24px" }}>
          <Image
            src="/LogoAir.png"
            alt="AirSentinel Logo"
            width={100}
            height={100}
            style={{ filter: "drop-shadow(0 6px 28px rgba(0,212,177,0.55))", margin: "0 auto" }}
            priority
          />
        </div>

        {/* Badge indabaX */}
        <div
          style={{
            display: "inline-block",
            background: "rgba(0,212,177,0.1)",
            border: "1px solid rgba(0,212,177,0.35)",
            borderRadius: "50px",
            padding: "6px 18px",
            fontSize: "12px",
            color: "#00d4b1",
            letterSpacing: "0.12em",
            marginBottom: "20px",
          }}
        >
          ▲ INDABAX CAMEROON 2026
        </div>

        {/* Titre principal */}
        <h1
          style={{
            fontSize: "clamp(28px, 5vw, 52px)",
            fontWeight: 800,
            lineHeight: 1.15,
            letterSpacing: "-0.03em",
            marginBottom: "16px",
            maxWidth: "700px",
            margin: "0 auto 16px",
          }}
        >
          AirSentinel :{" "}
          <span
            style={{
              background: "linear-gradient(135deg, #00d4b1, #0ea5e9)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            L&apos;IA au Service
          </span>
          <br />
          d&apos;un Air Plus Pur au Cameroun
        </h1>

        <p
          style={{
            fontSize: "clamp(14px, 2vw, 17px)",
            color: "rgba(224,242,254,0.65)",
            maxWidth: "520px",
            margin: "16px auto 36px",
            lineHeight: 1.7,
          }}
        >
          Visualisez, Analysez et Anticipez la Qualité de l&apos;Air sur Tout le Territoire
        </p>

        {/* CTA */}
        <div style={{ display: "flex", gap: "16px", justifyContent: "center", flexWrap: "wrap", marginTop: "10px" }}>
          <Link href="/register" className="btn-primary" style={{ padding: "14px 28px", fontSize: "16px" }}>
            S&apos;inscrire gratuitement
          </Link>
          <a
            href="#pilliers"
            style={{
              padding: "14px 28px",
              border: "1px solid rgba(0,212,177,0.4)",
              borderRadius: "50px",
              color: "#00d4b1",
              fontSize: "15px",
              textDecoration: "none",
              transition: "all 0.3s",
            }}
          >
            En savoir plus ↓
          </a>
        </div>

        {/* Stats */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "12px",
            flexWrap: "wrap",
            marginTop: "52px",
          }}
        >
          <StatBadge value="40" label="Villes" />
          <StatBadge value="10" label="Régions" />
          <StatBadge value="50 760" label="Observations" />
          <StatBadge value="J+3" label="Prédictions" />
        </div>
      </section>

      {/* ── NOS PILLIERS ────────────────────────────────────────────── */}
      <section
        id="pilliers"
        style={{
          position: "relative",
          zIndex: 1,
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "80px 24px",
        }}
      >
        <h2
          style={{
            fontSize: "clamp(22px, 3vw, 34px)",
            fontWeight: 800,
            marginBottom: "40px",
            color: "#e0f2fe",
          }}
        >
          Nos Piliers Stratégiques
        </h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "24px",
          }}
        >
          <PillarCard
            icon={<BrainCircuit size={28} />}
            title="Anticipation IA"
            description="Prédiction de la concentration PM2.5 à J+1 grâce à un modèle de régression entraîné sur 28 variables météo et historiques. ARIMA par zone pour les tendances à J+3."
          >
            <MiniChart />
          </PillarCard>

          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <PillarCard
              icon={<MapIcon size={28} />}
              title="Cartographie Interactive"
              description="Visualisation géospatiale en temps réel de la qualité de l'air dans les 40 grandes villes camerounaises avec l'Indice de Risque Sanitaire (IRS) par zone."
            />
            <PillarCard
              icon={<ShieldAlert size={28} />}
              title="Indice de Risque Sanitaire"
              description="Algorithme exclusif combinant PM2.5, CO, Dust, UV et Ozone via PCA pour calculer un score IRS : Faible · Modéré · Élevé · Critique."
            />
          </div>

          <div style={{ display: "flex", alignItems: "center" }}>
            <CameroonMap />
          </div>
        </div>
      </section>

      {/* ── TECH STACK ──────────────────────────────────────────────── */}
      <section
        id="techstack"
        style={{
          position: "relative",
          zIndex: 1,
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "60px 24px 80px",
          textAlign: "center",
        }}
      >
        <h2
          style={{
            fontSize: "clamp(20px, 3vw, 30px)",
            fontWeight: 800,
            marginBottom: "10px",
            color: "#e0f2fe",
          }}
        >
          Tech-Stack
        </h2>
        <p style={{ color: "rgba(224,242,254,0.5)", marginBottom: "36px", fontSize: "14px" }}>
          Des technologies éprouvées pour une performance de production
        </p>

        <div className="flex flex-wrap justify-center gap-6 mt-12">
          <TechBadge name="FastAPI" icon={<Zap size={24} />} />
          <TechBadge name="Supabase" icon={<Database size={24} />} />
          <TechBadge name="Scikit-Learn" icon={<Cpu size={24} />} />
          <TechBadge name="Docker" icon={<Boxes size={24} />} />
          <TechBadge name="Next.js" icon={<Layers size={24} />} />
          <TechBadge name="PostgreSQL" icon={<Database size={24} />} />
        </div>
      </section>

      {/* ── TÉMOIGNAGE ──────────────────────────────────────────────── */}
      <section
        style={{
          position: "relative",
          zIndex: 1,
          maxWidth: "700px",
          margin: "0 auto",
          padding: "0 24px 100px",
          textAlign: "center",
        }}
      >
        <div
          className="glass-card"
          style={{ padding: "36px 40px", borderColor: "rgba(0,212,177,0.3)" }}
        >
          <div style={{ fontSize: "40px", color: "#00d4b1", marginBottom: "16px", lineHeight: 1 }}>&ldquo;</div>
          <p
            style={{
              fontSize: "16px",
              lineHeight: 1.8,
              color: "rgba(224,242,254,0.85)",
              fontStyle: "italic",
              marginBottom: "24px",
            }}
          >
            AirSentinel représente une avancée majeure pour la santé publique au Cameroun. 
            Grâce à l&apos;intelligence artificielle, nous pouvons désormais anticiper les 
            épisodes de pollution et protéger les populations les plus vulnérables.
          </p>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "14px" }}>
            <div
              className="w-14 h-14 rounded-full border-2 border-[var(--teal)]/30 flex items-center justify-center bg-slate-800 text-[var(--teal)] shadow-[0_0_20px_rgba(0,212,177,0.2)]"
            >
              <Code size={28} />
            </div>
            <div style={{ textAlign: "left" }}>
              <div style={{ fontWeight: 700, color: "#e0f2fe", fontSize: "15px" }}>
                FOFACK ALEMDJOU HENRI JOEL
              </div>
              <div style={{ fontSize: "12px", color: "rgba(224,242,254,0.5)" }}>
                4ième année Génie Informatique, ENSPY
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER CLASSIC ───────────────────────────────────────────────────── */}
      <footer
        style={{
          position: "relative",
          zIndex: 1,
          textAlign: "center",
          padding: "40px 24px",
          borderTop: "1px solid rgba(0,212,177,0.12)",
          color: "rgba(224,242,254,0.3)",
          fontSize: "12px",
          letterSpacing: "0.06em",
        }}
      >
        <div style={{ marginBottom: "16px", display: "flex", justifyContent: "center", gap: "20px" }}>
          <span style={{ color: "rgba(0,212,177,0.8)", fontWeight: 600 }}>AirSentinel © 2026</span>
          <a href="#" style={{ color: "rgba(224,242,254,0.5)", textDecoration: "none" }}>Confidentialité</a>
          <a href="#" style={{ color: "rgba(224,242,254,0.5)", textDecoration: "none" }}>Conditions</a>
        </div>
        IndabaX Cameroon 2026 · DPA Green Tech · ISSEA · ENSP Yaoundé<br/>
        <span style={{ color: "rgba(0,212,177,0.55)", display: "block", marginTop: "8px" }}>17 mars → 7 avril 2026</span>
      </footer>
    </main>
  );
}
