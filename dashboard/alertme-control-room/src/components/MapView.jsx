import React from 'react';
import { MapPin, Layers, Crosshair } from 'lucide-react';

export default function MapView({ incidents, selectedIncidentId, onSelectIncident }) {
  // Filter out completed/false records to focus strictly on active control risks
  const activeIncidents = incidents.filter(
    (i) => i.status !== 'Resolved' && i.status !== 'False Alert'
  );

  const selectedIncident = incidents.find((i) => i.id === selectedIncidentId);

  // Status utility for card border tracking inside the sidebar layout
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Under Review': return 'bg-orange-50 text-orange-600 border-orange-200';
      case 'Verified': return 'bg-blue-50 text-blue-600 border-blue-200';
      case 'Dispatched': return 'bg-red-50 text-red-600 border-red-200';
      default: return 'bg-slate-50 text-slate-500 border-slate-200';
    }
  };

  return (
    <div className="h-full w-full flex relative bg-controlBg overflow-hidden">
      
      {/* LEFT AREA: FULL SCREEN TACTICAL GRID MAP VIEW */}
      <div className="flex-1 bg-slate-100 relative flex items-center justify-center overflow-hidden">
        {/* Tactical grid background effect lines */}
        <div className="absolute inset-0 opacity-[0.5] bg-[linear-gradient(to_right,#E2E8F0_1px,transparent_1px),linear-gradient(to_bottom,#E2E8F0_1px,transparent_1px)] bg-[size:40px_40px]"></div>
        <div className="absolute inset-0 opacity-[0.03] bg-[radial-gradient(#E03616_2px,transparent_2px)] bg-[size:20px_20px]"></div>

        {/* HUD Map Floating Info Box */}
        <div className="absolute top-4 left-4 bg-controlCard border border-controlBorder rounded-xl p-4 shadow-sm z-10 max-w-xs backdrop-blur-sm">
          <div className="flex items-center space-x-2 text-controlText font-bold text-xs uppercase tracking-wider mb-2">
            <Layers className="w-4 h-4 text-controlPrimary" />
            <span>Tactical Map Matrix</span>
          </div>
          <p className="text-[11px] text-controlMuted leading-normal font-medium">
            Plotting operational incident variables over the active operational area. Click any telemetry marker to inspect logs.
          </p>
          <div className="mt-3 pt-2 border-t border-controlBorder flex justify-between text-[10px] font-mono text-controlMuted font-bold">
            <span>Active Pins: {activeIncidents.length}</span>
            <span>Grid Status: Nom</span>
          </div>
        </div>

        {/* GEOSPATIAL MAP INCIDENT MARKER PLOTS */}
        {activeIncidents.map((incident, idx) => {
          const isSelected = incident.id === selectedIncidentId;
          
          // Deterministic coordinate plotting matrix anchors for the presentation canvas
          const topPercent = 30 + (idx * 16);
          const leftPercent = 25 + (idx * 22);

          let pinColor = 'text-orange-500';
          if (incident.status === 'Verified') pinColor = 'text-blue-500';
          if (incident.status === 'Dispatched') pinColor = 'text-red-500';

          return (
            <div
              key={incident.id}
              onClick={() => onSelectIncident(incident.id)}
              className="absolute cursor-pointer transition-all duration-300 transform -translate-x-1/2 -translate-y-1/2 group z-20"
              style={{ top: `${topPercent}%`, left: `${leftPercent}%` }}
            >
              {/* Pulsing ring radar anchor below active pins */}
              <span className={`absolute -inset-2 rounded-full animate-ping opacity-30 pointer-events-none duration-1000 ${
                incident.status === 'Dispatched' ? 'bg-red-400' : incident.status === 'Verified' ? 'bg-blue-400' : 'bg-orange-400'
              }`}></span>

              <div className={`relative ${isSelected ? 'scale-125 drop-shadow-md' : 'hover:scale-110'}`}>
                <MapPin className={`w-9 h-9 ${pinColor}`} />
                {isSelected && (
                  <Crosshair className="w-4 h-4 text-white absolute top-1 left-2.5 opacity-90" />
                )}
              </div>

              {/* Minimal Pop Hover Label Flag tooltip */}
              <div className="absolute left-1/2 -translate-x-1/2 top-10 bg-controlCard border border-controlBorder text-[10px] font-bold px-2 py-1 rounded shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-30 font-sans text-controlText">
                {incident.type} ({incident.id.split('-')[2]})
              </div>
            </div>
          );
        })}

        {/* Center Mock Reference Compass Overlay Indicator */}
        <div className="absolute bottom-6 right-6 font-mono text-[10px] text-controlMuted font-bold select-none bg-controlCard px-2 py-1 rounded border border-controlBorder shadow-sm">
          SYS_LOC // LAGOS_NGA_CTR
        </div>
      </div>

      {/* RIGHT SIDEBAR: INTEGRATED REAL-TIME DETAIL PANEL LAYER */}
      {selectedIncident && (
        <div className="w-80 bg-controlCard border-l border-controlBorder h-full flex flex-col p-5 shadow-sm overflow-y-auto shrink-0 z-30 animate-fadeIn">
          <div className="flex justify-between items-start border-b border-controlBorder pb-4">
            <div>
              <h3 className="font-extrabold text-sm text-controlText tracking-tight leading-tight uppercase">
                {selectedIncident.type}
              </h3>
              <span className="text-[10px] font-mono text-controlMuted block mt-1">
                {selectedIncident.id}
              </span>
            </div>
            <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded border uppercase shrink-0 ${getStatusBadgeClass(selectedIncident.status)}`}>
              {selectedIncident.status === 'Under Review' ? 'Review' : selectedIncident.status}
            </span>
          </div>

          <div className="flex-1 py-4 space-y-4 text-xs">
            <div>
              <span className="text-[10px] uppercase font-bold text-controlMuted tracking-wider block mb-1">Coordinates</span>
              <p className="text-controlText font-mono flex items-center bg-controlBg px-2 py-1.5 rounded border border-controlBorder font-bold">
                <MapPin className="w-3.5 h-3.5 text-controlPrimary mr-1.5" />
                {selectedIncident.coordinates}
              </p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold text-controlMuted tracking-wider block mb-1">Location Context</span>
              <p className="text-controlText font-bold pl-1">{selectedIncident.locationName}</p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold text-controlMuted tracking-wider block mb-1">Situation Log</span>
              <p className="text-slate-800 bg-controlBg p-3 rounded-lg border border-controlBorder leading-relaxed italic font-medium">
                "{selectedIncident.description}"
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}