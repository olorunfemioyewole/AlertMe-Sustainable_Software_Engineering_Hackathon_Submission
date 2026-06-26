import React, { useState, useEffect } from 'react';
import { initialIncidents } from './mockData';
import MapView from './components/MapView'; // Import the new MapView layer
import { Shield, Radio, Layers, LogOut, Maximize2, Minimize2, MapPin, CheckCircle, AlertTriangle, UserX, RotateCcw } from 'lucide-react';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('feed'); // 'feed' | 'map' | 'settings'
  const [incidents, setIncidents] = useState(initialIncidents);
  const [selectedIncidentId, setSelectedIncidentId] = useState(initialIncidents[0]?.id || null);
  const [expandedIncidentId, setExpandedIncidentId] = useState(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [confirmationState, setConfirmationState] = useState({ targetStatus: null });

  // Mock live ingestion event trigger simulation
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const timer = setTimeout(() => {
      const liveAlert = {
        id: `ALT-20260626-${Math.floor(1000 + Math.random() * 9000)}`,
        type: "Communal Violence",
        locationName: "Lagos Island, Lagos",
        coordinates: "6.5170, 3.3930",
        timeAgo: "Just now",
        timestamp: new Date().toISOString(),
        status: "Under Review",
        description: "Clashes reported near market square perimeter. Avoid the axis.",
        credibilityWeight: "1.0",
        source: "Mobile app",
        isNew: true
      };
      
      setIncidents(prev => [liveAlert, ...prev]);
    }, 8000);

    return () => clearTimeout(timer);
  }, [isAuthenticated]);

  const selectedIncident = incidents.find(i => i.id === selectedIncidentId);

  const getStatusConfig = (status) => {
    switch (status) {
      case 'Under Review': return { bg: 'bg-orange-500/10 text-orange-500 border-orange-500/30', border: 'border-l-orange-500' };
      case 'Verified': return { bg: 'bg-blue-500/10 text-blue-500 border-blue-500/30', border: 'border-l-blue-500' };
      case 'Dispatched': return { bg: 'bg-red-500/10 text-red-500 border-red-500/30', border: 'border-l-red-500' };
      case 'Resolved': return { bg: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30', border: 'border-l-emerald-500' };
      case 'False Alert': return { bg: 'bg-gray-500/10 text-gray-400 border-gray-500/30', border: 'border-l-gray-500' };
      default: return { bg: 'bg-gray-500/10 text-gray-500 border-gray-500/30', border: 'border-l-gray-500' };
    }
  };

  const handleStatusChange = (status) => {
    setIncidents(prev => prev.map(item => 
      item.id === selectedIncidentId ? { ...item, status } : item
    ));
    setConfirmationState({ targetStatus: null });
  };

  // --- SCREEN 1: AUTH LOGOUT EXCLUSION BLOCK ---
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-controlBg flex flex-col justify-center items-center px-4">
        <div className="w-full max-w-md bg-controlCard border border-controlBorder rounded-xl p-8 shadow-2xl">
          <div className="flex justify-center mb-6">
            <div className="w-12 h-12 bg-controlPrimary/10 rounded-lg flex items-center justify-center border border-controlPrimary/20">
              <Shield className="w-6 h-6 text-controlPrimary" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-center text-white tracking-tight">Control Room Access</h2>
          <p className="text-sm text-gray-400 text-center mt-2 mb-8">Alert Me Dispatch Dashboard — Authorised Personnel Only</p>
          
          <form onSubmit={(e) => { e.preventDefault(); setIsAuthenticated(true); }} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Email address</label>
              <input type="email" required placeholder="name@domain.gov" className="w-full bg-controlBg border border-controlBorder rounded-lg px-4 py-3 text-white focus:outline-none focus:border-controlPrimary transition-colors text-sm"/>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Password</label>
              <input type="password" required placeholder="••••••••" className="w-full bg-controlBg border border-controlBorder rounded-lg px-4 py-3 text-white focus:outline-none focus:border-controlPrimary transition-colors text-sm"/>
            </div>
            <button type="submit" className="w-full bg-controlPrimary hover:bg-controlPrimary/90 text-white font-semibold py-3 px-4 rounded-lg transition-colors mt-6 text-sm">
              Sign In
            </button>
          </form>
          
          <p className="text-xs text-gray-500 text-center mt-6">
            Account access is granted by your system administrator.
          </p>
        </div>
      </div>
    );
  }

  // --- SCREEN 3: HIGH ATTENTION FULL SCREEN MODAL LAYER ---
  if (expandedIncidentId && selectedIncident) {
    return (
      <div className="min-h-screen bg-controlBg text-white p-8 flex flex-col">
        <div className="flex justify-between items-center mb-8 border-b border-controlBorder pb-4">
          <div className="flex items-center space-x-3">
            <span className={`px-3 py-1 text-xs font-bold uppercase rounded border ${getStatusConfig(selectedIncident.status).bg}`}>
              {selectedIncident.status}
            </span>
            <h1 className="text-2xl font-bold tracking-tight">{selectedIncident.type.toUpperCase()}</h1>
            <span className="text-sm text-gray-400 font-mono">Ref: {selectedIncident.id}</span>
          </div>
          <button 
            onClick={() => setExpandedIncidentId(null)}
            className="flex items-center space-x-2 bg-controlCard border border-controlBorder px-4 py-2 rounded-lg text-sm hover:text-controlPrimary transition-colors"
          >
            <Minimize2 className="w-4 h-4" />
            <span>Collapse View</span>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1">
          <div className="space-y-6 lg:col-span-1">
            <div className="bg-controlCard border border-controlBorder p-6 rounded-xl">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Incident Metadata</h3>
              <p className="text-sm text-gray-300">Reported: <span className="text-white font-medium">{selectedIncident.timeAgo}</span></p>
              <p className="text-sm text-gray-300 mt-1">Source Pipeline: <span className="text-white font-medium">{selectedIncident.source}</span></p>
            </div>
            <div className="bg-controlCard border border-controlBorder p-6 rounded-xl">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Reporter Profile</h3>
              <p className="text-sm text-gray-300">Credibility Weight: <span className="text-white font-mono">{selectedIncident.credibilityWeight}</span></p>
            </div>
            <div className="bg-controlCard border border-controlBorder p-6 rounded-xl">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Situation Context</h3>
              <p className="text-base text-gray-200 leading-relaxed bg-controlBg/50 p-4 rounded-lg border border-controlBorder">
                "{selectedIncident.description}"
              </p>
            </div>
          </div>
          <div className="lg:col-span-2 bg-controlCard border border-controlBorder rounded-xl overflow-hidden flex flex-col min-h-[400px]">
            <div className="p-4 border-b border-controlBorder flex justify-between items-center bg-controlBg/30">
              <span className="text-sm font-semibold text-gray-300 flex items-center"><MapPin className="w-4 h-4 text-controlPrimary mr-2"/> {selectedIncident.locationName} ({selectedIncident.coordinates})</span>
            </div>
            <div className="flex-1 bg-[#121824] flex items-center justify-center relative">
              <div className="absolute inset-0 opacity-[0.15] bg-[linear-gradient(to_right,#242C3D_1px,transparent_1px),linear-gradient(to_bottom,#242C3D_1px,transparent_1px)] bg-[size:30px_30px]"></div>
              <div className="text-center z-10">
                <div className="w-12 h-12 bg-controlPrimary/20 rounded-full flex items-center justify-center mx-auto mb-3 animate-bounce">
                  <MapPin className="w-6 h-6 text-controlPrimary" />
                </div>
                <p className="text-sm font-semibold text-gray-300">Expanded Target Map Vector Layout</p>
                <p className="text-xs font-mono text-gray-500 mt-1">Geographic Context Node Pin: {selectedIncident.coordinates}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-controlBg text-white flex flex-col">
      {/* HUD HEADER NAVBAR LAYER */}
      <header className="bg-controlCard border-b border-controlBorder px-6 py-4 flex justify-between items-center shrink-0">
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-3">
            <Shield className="w-6 h-6 text-controlPrimary" />
            <span className="font-bold text-lg tracking-tight uppercase">Alert Me <span className="text-gray-400 font-normal">Control</span></span>
          </div>
          <nav className="flex space-x-1 bg-controlBg p-1 rounded-lg border border-controlBorder">
            <button 
              onClick={() => setCurrentView('feed')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${currentView === 'feed' ? 'bg-controlPrimary text-white shadow' : 'text-gray-400 hover:text-white'}`}
            >
              Feed View
            </button>
            <button 
              onClick={() => setCurrentView('map')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all ${currentView === 'map' ? 'bg-controlPrimary text-white shadow' : 'text-gray-400 hover:text-white'}`}
            >
              Map View
            </button>
          </nav>
        </div>
        
        <div className="flex items-center space-x-6">
          <button 
            onClick={() => setCurrentView('settings')} 
            className={`text-xs uppercase tracking-wider font-semibold hover:text-white transition-colors ${currentView === 'settings' ? 'text-controlPrimary' : 'text-gray-400'}`}
          >
            System Configs
          </button>
          <button 
            onClick={() => setIsAuthenticated(false)}
            className="text-gray-400 hover:text-controlPrimary transition-colors flex items-center space-x-1 text-xs"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Exit Session</span>
          </button>
        </div>
      </header>

      {/* CORE CONTROL AREA */}
      <div className="flex-1 overflow-hidden">
        
        {/* ACTION WORKSPACE A: SCREEN 2 (LIVE DISPATCH LOG FEED ROW) */}
        {currentView === 'feed' && (
          <div className="h-full flex divide-x divide-controlBorder">
            <div className="w-full md:w-[420px] shrink-0 bg-controlBg flex flex-col h-full">
              <div className="p-4 border-b border-controlBorder space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-sm font-bold tracking-wider uppercase text-gray-400">Alert Me — Dispatch Feed</h2>
                  <div className="flex items-center space-x-1.5 bg-controlCard px-2.5 py-1 rounded-full border border-controlBorder">
                    <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse-fast"></span>
                    <span className="text-[10px] uppercase tracking-widest font-bold text-gray-300">Live</span>
                  </div>
                </div>
                <div className="flex gap-1 overflow-x-auto pb-1 text-xs scrollbar-none">
                  {['All', 'Under Review', 'Verified', 'Dispatched', 'Resolved', 'False Alert'].map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setActiveFilter(filter)}
                      className={`px-2.5 py-1 rounded-md shrink-0 border transition-all ${activeFilter === filter ? 'bg-white text-black border-white font-semibold' : 'bg-controlCard text-gray-400 border-controlBorder hover:text-white'}`}
                    >
                      {filter}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {incidents
                  .filter(i => activeFilter === 'All' || i.status === activeFilter)
                  .map((incident) => {
                    const isSelected = incident.id === selectedIncidentId;
                    const config = getStatusConfig(incident.status);
                    return (
                      <div
                        key={incident.id}
                        onClick={() => setSelectedIncidentId(incident.id)}
                        className={`cursor-pointer bg-controlCard rounded-lg p-4 border border-controlBorder border-l-4 ${config.border} transition-all duration-300 ${isSelected ? 'ring-1 ring-controlPrimary bg-controlCard/80' : 'hover:bg-controlCard/60'} ${incident.isNew ? 'animate-pulse bg-controlPrimary/5 border-controlPrimary/40' : ''}`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-sm font-bold text-white tracking-tight">{incident.type}</h3>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase border ${config.bg}`}>
                            {incident.status === 'Under Review' ? 'Review' : incident.status}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400">{incident.locationName}</p>
                        <div className="flex justify-between items-center mt-3 pt-2 border-t border-t-controlBorder/40">
                          <span className="text-[10px] font-mono text-gray-500">{incident.id}</span>
                          <span className="text-[10px] text-gray-400">{incident.timeAgo}</span>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>

            <div className="flex-1 bg-controlBg/40 h-full overflow-y-auto p-6">
              {selectedIncident ? (
                <div className="bg-controlCard border border-controlBorder rounded-xl p-6 shadow-xl space-y-6 max-w-4xl mx-auto">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-controlBorder pb-4 gap-4">
                    <div>
                      <div className="flex items-center space-x-3 mb-1">
                        <h1 className="text-xl font-extrabold tracking-tight text-white">{selectedIncident.type.toUpperCase()}</h1>
                        <span className={`text-xs px-2.5 py-0.5 rounded font-bold uppercase border ${getStatusConfig(selectedIncident.status).bg}`}>
                          {selectedIncident.status}
                        </span>
                      </div>
                      <div className="text-xs text-gray-400 font-mono">
                        Ref: {selectedIncident.id} · Reported {selectedIncident.timeAgo} via {selectedIncident.source}
                      </div>
                    </div>
                    <button 
                      onClick={() => setExpandedIncidentId(selectedIncident.id)}
                      className="self-start sm:self-center flex items-center space-x-1.5 bg-controlBg border border-controlBorder px-3 py-1.5 rounded-lg text-xs hover:text-controlPrimary transition-colors"
                    >
                      <Maximize2 className="w-3.5 h-3.5" />
                      <span>Expand Screen</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Location Context</h4>
                        <p className="text-sm font-semibold text-white flex items-center"><MapPin className="w-4 h-4 text-controlPrimary mr-1"/> {selectedIncident.locationName}</p>
                        <p className="text-xs font-mono text-gray-400 ml-5 mt-0.5">{selectedIncident.coordinates}</p>
                      </div>
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Reporter Verification Metric</h4>
                        <p className="text-sm text-gray-300">Credibility Weight Vector: <span className="font-mono text-white bg-controlBg px-1.5 py-0.5 border border-controlBorder rounded text-xs">{selectedIncident.credibilityWeight}</span></p>
                      </div>
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1.5">Description Logs</h4>
                        <p className="text-sm text-gray-300 bg-controlBg/80 p-4 rounded-lg border border-controlBorder border-l-2 border-l-controlPrimary leading-relaxed">
                          "{selectedIncident.description}"
                        </p>
                      </div>
                    </div>

                    <div className="bg-controlBg/60 border border-controlBorder rounded-xl flex flex-col items-center justify-center p-6 text-center min-h-[200px] relative overflow-hidden">
                      <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#242c3d_1px,transparent_1px)] [background-size:12px_12px]"></div>
                      <MapPin className="w-8 h-8 text-controlPrimary/40 mb-2 animate-pulse" />
                      <span className="text-xs font-semibold text-gray-400">Tactical Position Display Layer</span>
                      <span className="text-[10px] font-mono text-gray-500 mt-1">{selectedIncident.coordinates}</span>
                    </div>
                  </div>

                  <div className="border-t border-controlBorder pt-4 space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">Status Actions Control</h4>
                    
                    {confirmationState.targetStatus ? (
                      <div className="bg-controlPrimary/10 border border-controlPrimary/30 rounded-xl p-4 flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-sm text-gray-200">
                          <AlertTriangle className="w-4 h-4 text-controlPrimary" />
                          <span>Mark incident log tracking sequence as <span className="text-white font-bold underline uppercase">{confirmationState.targetStatus}</span>? Confirm Action ↓</span>
                        </div>
                        <div className="flex space-x-2">
                          <button 
                            onClick={() => handleStatusChange(confirmationState.targetStatus)}
                            className="bg-controlPrimary hover:bg-controlPrimary/90 text-white font-bold px-4 py-1.5 rounded-lg text-xs transition-colors"
                          >
                            Yes, Execute
                          </button>
                          <button 
                            onClick={() => setConfirmationState({ targetStatus: null })}
                            className="bg-controlBg border border-controlBorder hover:bg-controlCard text-gray-300 px-3 py-1.5 rounded-lg text-xs transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        <button 
                          onClick={() => setConfirmationState({ targetStatus: 'Verified' })}
                          className="bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white border border-blue-600/20 font-semibold py-2 px-3 rounded-lg text-xs transition-all flex items-center justify-center space-x-1"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Verify</span>
                        </button>
                        <button 
                          onClick={() => setConfirmationState({ targetStatus: 'Dispatched' })}
                          className="bg-red-600/10 hover:bg-red-600 text-red-400 hover:text-white border border-red-600/20 font-semibold py-2 px-3 rounded-lg text-xs transition-all flex items-center justify-center space-x-1"
                        >
                          <Radio className="w-3.5 h-3.5" />
                          <span>Dispatch</span>
                        </button>
                        <button 
                          onClick={() => setConfirmationState({ targetStatus: 'False Alert' })}
                          className="bg-gray-600/10 hover:bg-gray-600 text-gray-400 hover:text-white border border-gray-600/20 font-semibold py-2 px-3 rounded-lg text-xs transition-all flex items-center justify-center space-x-1"
                        >
                          <UserX className="w-3.5 h-3.5" />
                          <span>False Alert</span>
                        </button>
                        <button 
                          onClick={() => setConfirmationState({ targetStatus: 'Resolved' })}
                          className="bg-emerald-600/10 hover:bg-emerald-600 text-emerald-400 hover:text-white border border-emerald-600/20 font-semibold py-2 px-3 rounded-lg text-xs transition-all flex items-center justify-center space-x-1"
                        >
                          <RotateCcw className="w-3.5 h-3.5" />
                          <span>Resolved</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500 text-sm font-mono">Select an active incident report target element to investigate profiles.</div>
              )}
            </div>
          </div>
        )}

        {/* ACTION WORKSPACE B: SCREEN 4 (TACTICAL GEOSPATIAL MAP ROUTE) */}
        {currentView === 'map' && (
          <MapView 
            incidents={incidents}
            selectedIncidentId={selectedIncidentId}
            onSelectIncident={(id) => setSelectedIncidentId(id)}
          />
        )}

        {/* ACTION WORKSPACE C: SCREEN 5 (SYSTEM SETTINGS FRAME) */}
        {currentView === 'settings' && (
          <div className="p-8 max-w-2xl mx-auto space-y-6 animate-fadeIn">
            <h2 className="text-xl font-bold tracking-tight text-white border-b border-controlBorder pb-3">System Configurations</h2>
            
            <div className="bg-controlCard border border-controlBorder rounded-xl p-6 space-y-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Active Dispatch Profile Context</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm bg-controlBg/50 p-4 rounded-lg border border-controlBorder">
                <div>
                  <span className="text-xs text-gray-500 block mb-0.5">Operator Assigned Identity</span>
                  <span className="font-medium text-white">Command Station Agent Alpha</span>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block mb-0.5">Security Clearance Role</span>
                  <span className="font-medium text-controlPrimary font-semibold">Lead Field Incident Evaluator</span>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center bg-controlCard border border-controlBorder rounded-xl p-4">
              <span className="text-xs font-mono text-gray-500">Alert Me Control Room v1.0.0</span>
              <button 
                onClick={() => setIsAuthenticated(false)}
                className="bg-red-600/10 hover:bg-red-600 border border-red-600/20 text-red-400 hover:text-white px-4 py-2 rounded-lg text-xs font-bold transition-all shadow"
              >
                Sign Out
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}