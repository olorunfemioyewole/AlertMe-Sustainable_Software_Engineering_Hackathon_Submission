import React from 'react';
import { MapPin, Layers, Crosshair, Eye } from 'lucide-react';

export default function MapView({ incidents, selectedIncidentId, onSelectIncident }) {
  // Filter out completed/false records to focus strictly on active control risks
  const activeIncidents = incidents.filter(
    (i) => i.status !== 'Resolved' && i.status !== 'False Alert'
  );

  const selectedIncident = incidents.find((i) => i.id === selectedIncidentId);

  // Status utility for card border tracking inside the sidebar layout
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Under Review': return 'bg-orange-500/10 text-orange-500 border-orange-500/30';
      case 'Verified': return 'bg-blue-500/10 text-blue-500 border-blue-500/30';
      case 'Dispatched': return 'bg-red-500/10 text-red-500 border-red-500/30';
      default: return 'bg-gray-500/10 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="h-full w-full flex relative bg-controlBg overflow-hidden">
      
      {/* LEFT AREA: FULL SCREEN TACTICAL GRID MAP VIEW */}
      <div className="flex-1 bg-[#0e131f] relative flex items-center justify-center overflow-hidden">
        {/* Tactical grid background effect lines */}
        <div className="absolute inset-0 opacity-[0.15] bg-[linear-gradient(to_right,#242C3D_1px,transparent_1px),linear-gradient(to_bottom,#242C3D_1px,transparent_1px)] bg-[size:40px_40px]"></div>
        <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#E03616_2px,transparent_2px)] bg-[size:20px_20px]"></div>

        {/* HUD Map Floating Info Box */}
        <div className="absolute top-4 left-4 bg-controlCard/95 border border-controlBorder rounded-xl p-4 shadow-2xl z-10 max-w-xs backdrop-blur-sm">
          <div className="flex items-center space-x-2 text-gray-300 font-bold text-xs uppercase tracking-wider mb-2">
            <Layers className="w-4 h-4 text-controlPrimary" />
            <span>Tactical Map Matrix</span>
          </div>
          <p className="text-[11px] text-gray-400 leading-normal">
            Plotting operational incident variables over the active operational area. Click any telemetry marker to inspect logs.
          </p>
          <div className="mt-3 pt-2 border-t border-controlBorder/60 flex justify-between text-[10px] font-mono text-gray-500">
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
              <span className={`absolute -inset-2 rounded-full animate-ping opacity-20 pointer-events-none duration-1000 ${
                incident.status === 'Dispatched' ? 'bg-red-500' : incident.status === 'Verified' ? 'bg-blue-500' : 'bg-orange-500'
              }`}></span>

              <div className={`relative ${isSelected ? 'scale-125 drop-shadow-[0_0_8px_rgba(224,54,22,0.6)]' : 'hover:scale-110'}`}>
                <MapPin className={`w-9 h-9 ${pinColor}`} />
                {isSelected && (
                  <Crosshair className="w-4 h-4 text-white absolute top-1 left-2.5 animate-spin-slow opacity-80" />
                )}
              </div>

              {/* Minimal Pop Hover Label Flag tooltip */}
              <div className="absolute left-1/2 -translate-x-1/2 top-10 bg-controlCard border border-controlBorder text-[10px] font-bold px-2 py-1 rounded shadow-xl whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-30 font-sans text-gray-200">
                {incident.type} ({incident.id.split('-')[2]})
              </div>
            </div>
          );
        })}

        {/* Center Mock Reference Compass Overlay Indicator */}
        <div className="absolute bottom-6 right-6 font-mono text-[10px] text-gray-600 select-none bg-controlBg/40 px-2 py-1 rounded border border-controlBorder/40">
          SYS_LOC // LAGOS_NGA_CTR
        </div>
      </div>

      {/* RIGHT SIDEBAR: INTEGRATED REAL-TIME DETAIL PANEL LAYER */}
      {selectedIncident && (
        <div className="w-80 bg-controlCard border-l border-controlBorder h-full flex flex-col p-5 shadow-2xl overflow-y-auto shrink-0 z-30 animate-fadeIn">
          <div className="flex justify-between items-start border-b border-controlBorder pb-4">
            <div>
              <h3 className="font-extrabold text-sm text-white tracking-tight leading-tight uppercase">
                {selectedIncident.type}
              </h3>
              <span className="text-[10px] font-mono text-gray-500 block mt-1">
                {selectedIncident.id}
              </span>
            </div>
            <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded border uppercase shrink-0 ${getStatusBadgeClass(selectedIncident.status)}`}>
              {selectedIncident.status === 'Under Review' ? 'Review' : selectedIncident.status}
            </span>
          </div>

          <div className="flex-1 py-4 space-y-4 text-xs">
            <div>
              <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider block mb-1">Coordinates</span>
              <p className="text-gray-200 font-mono flex items-center bg-controlBg px-2 py-1.5 rounded border border-controlBorder">
                <MapPin className="w-3.5 h-3.5 text-controlPrimary mr-1.5" />
                {selectedIncident.coordinates}
              </p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider block mb-1">Location Context</span>
              <p className="text-gray-300 font-medium pl-1">{selectedIncident.locationName}</p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider block mb-1">Situation Log</span>
              <p className="text-gray-300 bg-controlBg p-3 rounded-lg border border-controlBorder leading-relaxed italic">
                "{selectedIncident.description}"
              </p>
            </div>

            <div className="bg-controlBg/30 p-3 rounded-lg border border-controlBorder/50 space-y-1 text-[11px]">
              <div className="flex justify-between text-gray-400">
                <span>Reporter Weight:</span>
                <span className="font-mono text-gray-200">{selectedIncident.credibilityWeight}</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Timestamp:</span>
                <span className="text-gray-200">{selectedIncident.timeAgo}</span>
              </div>
            </div>
          </div>

          {/* Core view redirect handoff mechanism back to dispatch stack */}
          <div className="pt-2">
            <p className="text-[10px] text-gray-500 text-center mb-2 font-mono">To adjust status parameters, swap views</p>
          </div>
        </div>
      )}
    </div>
  );
}