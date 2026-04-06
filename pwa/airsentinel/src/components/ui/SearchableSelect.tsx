"use client";

import React, { useState, useRef, useEffect } from "react";
import { Search, ChevronDown, Check, MapPin, X } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface SearchableSelectProps {
  options: string[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
}

export default function SearchableSelect({
  options,
  value,
  onChange,
  placeholder = "Rechercher une ville...",
  label = "Ville"
}: SearchableSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredOptions = options.filter((option) =>
    option.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-1.5 w-full relative" ref={containerRef}>
      {label && <label className="text-[13px] text-gray-300 ml-1">{label}</label>}
      
      <div 
        className={cn(
          "relative group cursor-pointer transition-all duration-300",
          "w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl px-4 flex items-center justify-between",
          isOpen ? "border-[var(--teal)] ring-1 ring-[var(--teal)]/50" : "hover:bg-[#1e293b]/60"
        )}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <MapPin className="w-4 h-4 text-[var(--teal)] flex-shrink-0" />
          <span className={cn(
            "text-sm truncate",
            value ? "text-white" : "text-gray-500"
          )}>
            {value || "Sélectionnez votre ville"}
          </span>
        </div>
        
        <ChevronDown className={cn(
          "w-4 h-4 text-gray-400 transition-transform duration-300",
          isOpen && "rotate-180"
        )} />
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-[calc(100%+8px)] left-0 w-full z-50 animate-in fade-in zoom-in-95 duration-200">
          <div className="glass-card !bg-[#0f172a]/95 !border-white/10 shadow-2xl rounded-2xl overflow-hidden backdrop-blur-xl">
            
            {/* Search Input */}
            <div className="p-3 border-b border-white/5 relative">
              <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                autoFocus
                type="text"
                className="w-full h-9 bg-white/5 border border-white/10 rounded-lg pl-9 pr-4 text-sm text-white focus:outline-none focus:border-[var(--teal)]/50 transition-all placeholder:text-gray-600"
                placeholder={placeholder}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onClick={(e) => e.stopPropagation()}
              />
              {search && (
                <button 
                  className="absolute right-6 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSearch("");
                  }}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Options List */}
            <div className="max-h-[220px] overflow-y-auto custom-scrollbar p-1">
              {filteredOptions.length > 0 ? (
                filteredOptions.map((option) => (
                  <div
                    key={option}
                    className={cn(
                      "group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-all",
                      value === option ? "bg-[var(--teal)]/10 text-[var(--teal)]" : "text-gray-300 hover:bg-white/5 hover:text-white"
                    )}
                    onClick={(e) => {
                      e.stopPropagation();
                      onChange(option);
                      setIsOpen(false);
                      setSearch("");
                    }}
                  >
                    <span className="text-sm font-medium">{option}</span>
                    {value === option && <Check className="w-4 h-4" />}
                  </div>
                ))
              ) : (
                <div className="p-8 text-center">
                  <p className="text-sm text-gray-500">Aucune ville trouvée</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
