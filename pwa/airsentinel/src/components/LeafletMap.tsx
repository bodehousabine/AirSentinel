"use client";

import { useEffect, useState, useCallback } from "react";
import L from "leaflet";
import { 
  MapContainer, 
  TileLayer, 
  CircleMarker, 
  Popup, 
  LayersControl,
  useMap
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import { Navigation, Search, ZoomIn, ZoomOut, X, MapPin, Compass, Loader2 } from "lucide-react";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";

import mapService from "../services/mapService";
import { VillePoint } from "../types/map";
import { useVille } from "../context/VilleContext";

// ── Sous-composant : REAL HEATMAP LAYER ──────────────────────────────────────

function HeatmapLayer({ points }: { points: VillePoint[] }) {
  const map = useMap();

  useEffect(() => {
    if (points.length === 0) return;
    
    const heatData: [number, number, number][] = points
      .filter(p => p.lat !== null && p.lon !== null)
      .map(c => [c.lat!, c.lon!, c.pm25_moyen / 100]);
      
    // @ts-expect-error - Leaflet.heat plugin not typed
    const heatLayer = L.heatLayer(heatData, {
      radius: 40,
      blur: 25,
      maxZoom: 14,
      gradient: { 0.2: 'green', 0.4: 'yellow', 0.6: 'orange', 0.8: 'red', 1.0: 'purple' }
    });

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, points]);

  return null;
}

// ── Sous-composant : PWA SEARCH BAR ─────────────────────────────────────────

function MapSearch({ points, onSelect, onSelectVille }: { points: VillePoint[], onSelect: (lat: number, lon: number) => void, onSelectVille: (ville: string) => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<VillePoint[]>([]);

  const handleSearch = (val: string) => {
    setQuery(val);
    if (val.length > 1) {
      setResults(points.filter(c => c.city.toLowerCase().includes(val.toLowerCase())));
    } else {
      setResults([]);
    }
  };

  return (
    <div className="absolute top-[70px] left-0 right-0 z-[1000] flex justify-center px-4 pointer-events-none">
      <div className="w-full max-w-[400px] pointer-events-auto">
        <div className="relative group">
          <div className="absolute inset-x-0 -bottom-1 h-px bg-gradient-to-r from-transparent via-[#00d4b1]/50 to-transparent blur-sm opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
          <div className="flex items-center bg-white border border-gray-100 rounded-3xl shadow-[0_15px_40px_rgba(0,0,0,0.12)] px-5 py-4 placeholder:text-gray-400">
            <Search size={22} className="text-[#00d4b1] mr-3 shrink-0" />
            <input
              type="text"
              placeholder="Rechercher une ville..."
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              className="bg-transparent border-none outline-none text-gray-800 text-base font-medium w-full placeholder:text-gray-400"
            />
            {query && (
              <button 
                onClick={() => handleSearch("")}
                className="p-1 hover:bg-gray-50 rounded-full"
              >
                <X size={20} className="text-gray-400" />
              </button>
            )}
          </div>

          {results.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-3 bg-white/95 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl overflow-hidden py-2 max-h-[60vh] overflow-y-auto animate-in fade-in slide-in-from-top-2 duration-300">
              {results.map((point) => (
                <button
                  key={point.city}
                  onClick={() => {
                    onSelectVille(point.city);
                    if (point.lat && point.lon) onSelect(point.lat, point.lon);
                    setQuery("");
                    setResults([]);
                  }}
                  className="w-full text-left px-6 py-4 hover:bg-[#00d4b1]/5 flex items-center gap-4 transition-colors group border-b border-gray-50 last:border-0"
                >
                  <div className="w-10 h-10 rounded-xl bg-[#00d4b1]/10 flex items-center justify-center text-[#00d4b1] shrink-0">
                    <MapPin size={20} />
                  </div>
                  <div>
                    <div className="text-sm font-bold text-gray-800">{point.city}</div>
                    <div className="text-[10px] text-gray-500 font-bold uppercase tracking-tight flex items-center gap-2">
                       PM2.5: <span className="text-[#00d4b1]">{point.pm25_moyen} µg/m³</span>
                       <span className="w-1 h-1 rounded-full bg-gray-200"></span>
                       {point.irs_label || "Qualité"}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Sous-composant : PWA OVERLAY CONTROLS ───────────────────────────────────

function MapOverlayControls({ map }: { map: L.Map | null }) {
  const [locating, setLocating] = useState(false);

  const handleZoomIn = () => map?.zoomIn();
  const handleZoomOut = () => map?.zoomOut();

  const handleLocate = useCallback(() => {
    if (!map) return;
    if (!navigator.geolocation) {
      alert("La géolocalisation n'est pas supportée par votre navigateur.");
      return;
    }
    
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocating(false);
        const { latitude, longitude } = position.coords;
        map.flyTo([latitude, longitude], 14, { animate: true, duration: 1.5 });
      },
      (error) => {
        setLocating(false);
        console.error("Geolocation error:", error);
        alert("Impossible d'accéder à votre position.");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  }, [map]);

  const handleReset = () => {
    map?.flyTo([7.3697, 12.3547], 6, { animate: true, duration: 1.2 });
  };

  return (
    <div className="absolute bottom-28 right-6 z-[1001] flex flex-col gap-4 items-center">
      <div className="flex flex-col gap-3">
        <button
          onClick={handleLocate}
          disabled={locating}
          className={`w-14 h-14 bg-[#00d4b1] text-white rounded-2xl shadow-xl flex items-center justify-center transition-all active:scale-90 ${locating ? 'opacity-70' : ''}`}
        >
          <Navigation size={26} fill="white" className={locating ? 'animate-spin' : ''} />
        </button>
        
        <button
          onClick={handleReset}
          className="w-14 h-14 bg-white text-[#00d4b1] rounded-2xl shadow-xl flex items-center justify-center border border-gray-100 transition-all active:scale-95"
        >
          <Compass size={26} />
        </button>
      </div>

      <div className="flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden divide-y divide-gray-50">
        <button onClick={handleZoomIn} className="w-14 h-14 flex items-center justify-center text-gray-700 hover:bg-gray-50 active:bg-gray-100 transition-all">
          <ZoomIn size={24} strokeWidth={2.5} />
        </button>
        <button onClick={handleZoomOut} className="w-14 h-14 flex items-center justify-center text-gray-700 hover:bg-gray-50 active:bg-gray-100 transition-all">
          <ZoomOut size={24} strokeWidth={2.4} />
        </button>
      </div>
    </div>
  );
}

// ── Composant Principal ──────────────────────────────────────────────────────

export default function LeafletMap() {
  const cameroonCenter: [number, number] = [7.3697, 12.3547];
  const [map, setMap] = useState<L.Map | null>(null);
  const [points, setPoints] = useState<VillePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const { selectVille } = useVille();

  useEffect(() => {
    const fetchPoints = async () => {
      try {
        const data = await mapService.getMapPoints();
        setPoints(data);
      } catch (err) {
        console.error("Erreur chargement points carte:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPoints();
  }, []);

  useEffect(() => {
    // @ts-expect-error - Leaflet internal method for icon URLs
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    });
  }, []);

  const handleSelectCity = (lat: number, lon: number) => {
    map?.flyTo([lat, lon], 12, { animate: true, duration: 1.5 });
  };

  return (
    <div className="w-full h-full relative overflow-hidden">
      <MapSearch points={points} onSelect={handleSelectCity} onSelectVille={selectVille} />
      <MapOverlayControls map={map} />

      {loading && (
        <div className="absolute inset-0 z-[2000] bg-[#020c18]/40 backdrop-blur-sm flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
             <Loader2 className="w-10 h-10 text-[#00d4b1] animate-spin" />
             <p className="text-white text-sm font-medium">Synchronisation des stations...</p>
          </div>
        </div>
      )}

      <MapContainer 
        center={cameroonCenter} 
        zoom={6} 
        minZoom={3}
        maxZoom={18}
        zoomControl={false}
        ref={(instance) => { if (instance) setMap(instance); }}
        style={{ width: "100%", height: "100%" }}
        className="bg-[#020c18] !z-0"
      >
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="🗺️ Plan (OSM)">
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="📡 Satellite">
            <TileLayer
              attribution='&copy; Esri'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>

          <LayersControl.Overlay checked name="🔥 Heatmap">
            <HeatmapLayer points={points} />
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="📍 Stations">
              {points.filter(p => p.lat !== null && p.lon !== null).map((point) => (
                <CircleMarker
                  key={point.city}
                  center={[point.lat!, point.lon!]}
                  radius={6}
                  pathOptions={{
                    fillColor: point.irs_color || "#22c55e",
                    color: "white",
                    weight: 2,
                    fillOpacity: 0.8,
                  }}
                >
                  <Popup>
                    <div className="min-w-[160px] p-1 font-sans text-slate-800">
                      <div className="text-lg font-bold mb-1 border-b pb-1">{point.city}</div>
                      
                      <div className="space-y-2 mt-2">
                        {/* Section IRS */}
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">Risque (IRS)</span>
                          <div className="flex items-center gap-2">
                            <span 
                              className="px-2 py-0.5 rounded text-[11px] font-bold text-white uppercase"
                              style={{ backgroundColor: point.irs_color || "#4CAF50" }}
                            >
                              {point.irs_label || "Stable"}
                            </span>
                            <span className="text-xs font-medium text-gray-500">
                              {point.irs_moyen ? point.irs_moyen.toFixed(2) : "0.00"}
                            </span>
                          </div>
                        </div>

                        {/* Section PM2.5 */}
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">Pollution (PM2.5)</span>
                          <div className="flex items-center gap-1.5 bg-gray-50 p-1.5 rounded-lg border border-gray-100">
                            <div className="w-2 h-2 rounded-full bg-[#00d4b1]"></div>
                            <span className="text-sm font-bold text-gray-800">
                              {point.pm25_moyen} <span className="text-[10px] font-normal text-gray-500">µg/m³</span>
                            </span>
                          </div>
                        </div>
                      </div>

                      <button className="w-full mt-3 py-2 bg-[#020c18] text-white rounded-xl text-xs font-bold hover:bg-[#00d4b1] transition-colors active:scale-95">
                        Détails & Prévisions
                      </button>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
          </LayersControl.Overlay>
        </LayersControl>
      </MapContainer>

      {/* ── Légende PWA Premium ── */}
      <div className="absolute bottom-24 left-6 z-[1000] bg-slate-900/40 backdrop-blur-xl border border-white/10 rounded-3xl p-5 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div className="flex flex-col gap-4">
          <div className="space-y-1">
            <h4 className="text-[10px] font-black text-[var(--teal)] uppercase tracking-[0.15em] leading-none">
              Indice IRS
            </h4>
            <p className="text-[9px] text-gray-400 font-medium">Niveau de risque santé</p>
          </div>
          
          <div className="grid grid-cols-1 gap-3">
            {[
              { label: "Faible", color: "#4CAF50", desc: "Air pur & sain" },
              { label: "Modéré", color: "#FFC107", desc: "Sensibilité légère" },
              { label: "Élevé", color: "#FF5722", desc: "Pollution active" },
              { label: "Critique", color: "#B71C1C", desc: "Danger sanitaire" },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-3">
                <div 
                  className="w-3 h-3 rounded-full border-2 border-white/20 shadow-[0_0_8px_rgba(0,0,0,0.2)]" 
                  style={{ backgroundColor: item.color, boxShadow: `0 0 12px ${item.color}44` }} 
                />
                <div className="flex flex-col">
                  <span className="text-xs font-bold text-white leading-none mb-0.5">
                    {item.label}
                  </span>
                  <span className="text-[9px] text-gray-500 font-medium">
                    {item.desc}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
        .leaflet-container { z-index: 0 !important; }
        .leaflet-popup-content-wrapper { border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
        .leaflet-control-layers { 
          border-radius: 20px !important; 
          border: none !important; 
          box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
          margin-top: 90px !important;
          margin-right: 20px !important;
        }
      `}} />
    </div>
  );
}
