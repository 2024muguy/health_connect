'use client';

import { useEffect, useMemo, useState } from 'react';
import dynamic from 'next/dynamic';
import { Navigation, MapPin, Clock, Route } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

// Leaflet must be loaded client-side only
const MapContainer = dynamic(
  () => import('react-leaflet').then((m) => m.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then((m) => m.TileLayer),
  { ssr: false }
);
const Marker = dynamic(
  () => import('react-leaflet').then((m) => m.Marker),
  { ssr: false }
);
const Popup = dynamic(
  () => import('react-leaflet').then((m) => m.Popup),
  { ssr: false }
);
const Polyline = dynamic(
  () => import('react-leaflet').then((m) => m.Polyline),
  { ssr: false }
);

// Locations
const CLINICS = [
  {
    id: 'central',
    name: 'HealthConnect Central Clinic',
    address: '14 Wellness Avenue, Central District',
    lat: -1.2921,
    lng: 36.8219, // Nairobi center
  },
  {
    id: 'lakeside',
    name: 'HealthConnect Lakeside Clinic',
    address: '8 Care Street, Lakeside District',
    lat: -1.3197,
    lng: 36.7073,
  },
];

// Destination — Ongata Rongai
const ONGATA_RONGAI = {
  name: 'Ongata Rongai',
  lat: -1.3975,
  lng: 36.7441,
};

interface ClinicMapProps {
  onDistanceCalculated?: (distanceKm: number, durationMin: number) => void;
}

export function ClinicMap({ onDistanceCalculated }: ClinicMapProps) {
  const [selectedClinic, setSelectedClinic] = useState(CLINICS[0]);
  const [routeData, setRouteData] = useState<{
    distance: number;
    duration: number;
    coordinates: [number, number][];
  } | null>(null);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);

  // Load Leaflet icon fix (marker icons need a patch for Next.js)
  useEffect(() => {
    import('leaflet').then((L) => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });
    });
  }, []);

  // Get user's location
  useEffect(() => {
    if (typeof window === 'undefined' || !navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => setUserLocation([pos.coords.latitude, pos.coords.longitude]),
      () => setUserLocation(null),
      { timeout: 5000 }
    );
  }, []);

  // Calculate route using OSRM (free, no API key)
  const calculateRoute = async (from: [number, number], to: [number, number]) => {
    try {
      const url = `https://router.project-osrm.org/route/v1/driving/${from[1]},${from[0]};${to[1]},${to[0]}?overview=full&geometries=geojson`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.routes && data.routes[0]) {
        const route = data.routes[0];
        const coords: [number, number][] = route.geometry.coordinates.map(
          (c: [number, number]) => [c[1], c[0]]
        );
        const distanceKm = route.distance / 1000;
        const durationMin = route.duration / 60;

        setRouteData({
          distance: distanceKm,
          duration: durationMin,
          coordinates: coords,
        });

        onDistanceCalculated?.(distanceKm, durationMin);
      }
    } catch (err) {
      console.error('[ClinicMap] route failed', err);
    }
  };

  const handleNavigate = () => {
    const origin = userLocation ?? [selectedClinic.lat, selectedClinic.lng];
    calculateRoute(origin, [ONGATA_RONGAI.lat, ONGATA_RONGAI.lng]);
  };

  const handleOpenInMaps = () => {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${ONGATA_RONGAI.lat},${ONGATA_RONGAI.lng}`;
    window.open(url, '_blank');
  };

  const center: [number, number] = useMemo(
    () => [selectedClinic.lat, selectedClinic.lng],
    [selectedClinic]
  );

  return (
    <div className="panel p-4 md:p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <MapPin size={18} className="text-primary" />
            Find Us & Get Directions
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Navigate to {ONGATA_RONGAI.name} from our clinic
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleNavigate}
            className="button button-primary text-xs h-9"
            data-testid="button-navigate"
          >
            <Route size={14} /> Get Route
          </button>
          <button
            onClick={handleOpenInMaps}
            className="button text-xs h-9 border border-border"
            data-testid="button-open-maps"
          >
            <Navigation size={14} /> Open in Maps
          </button>
        </div>
      </div>

      {/* Clinic selector */}
      <div className="flex gap-2 mb-3 overflow-x-auto">
        {CLINICS.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelectedClinic(c)}
            className={`px-3 py-1.5 rounded-lg text-xs whitespace-nowrap transition-colors ${
              selectedClinic.id === c.id
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted hover:bg-muted/80'
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      {/* Map */}
      <div className="rounded-xl overflow-hidden border border-border" style={{ height: 400 }}>
        <MapContainer
          center={center}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Clinic markers */}
          {CLINICS.map((c) => (
            <Marker key={c.id} position={[c.lat, c.lng]}>
              <Popup>
                <strong>{c.name}</strong>
                <br />
                {c.address}
              </Popup>
            </Marker>
          ))}

          {/* Destination marker */}
          <Marker position={[ONGATA_RONGAI.lat, ONGATA_RONGAI.lng]}>
            <Popup>
              <strong>Destination: {ONGATA_RONGAI.name}</strong>
            </Popup>
          </Marker>

          {/* User location */}
          {userLocation && (
            <Marker position={userLocation}>
              <Popup>You are here</Popup>
            </Marker>
          )}

          {/* Route line */}
          {routeData && (
            <Polyline
              positions={routeData.coordinates}
              pathOptions={{ color: '#0ea5e9', weight: 4 }}
            />
          )}
        </MapContainer>
      </div>

      {/* Route info */}
      {routeData && (
        <div className="mt-3 flex items-center gap-4 p-3 rounded-lg bg-primary/5 border border-primary/20">
          <div className="flex items-center gap-2 text-xs">
            <Route size={14} className="text-primary" />
            <span>
              <strong>{routeData.distance.toFixed(1)} km</strong>
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <Clock size={14} className="text-primary" />
            <span>
              <strong>{Math.round(routeData.duration)} min</strong> drive
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
