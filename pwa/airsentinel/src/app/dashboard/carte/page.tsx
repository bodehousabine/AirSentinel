
"use client";

import dynamic from "next/dynamic";

// Ensure we don't render placeholder on server to avoid hydration mismatch
const MapComponent = dynamic(
  () => import("../../../components/LeafletMap"),
  { 
    ssr: false, 
    loading: () => (
      <div className="w-full h-[calc(100vh-64px)] bg-[#020c18] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-[#00d4b1] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-[#e0f2fe] text-sm animate-pulse">Chargement de la carte satellitaire...</p>
        </div>
      </div>
    )
  }
);

export default function CartePage() {
  return (
    <main className="w-full bg-[#020c18]">
      {/* We assume the header is handled by the main layout, so we just fill the rest of the height */}
      <div className="w-full h-[calc(100vh-64px)] relative">
        <MapComponent />
      </div>
    </main>
  );
}
