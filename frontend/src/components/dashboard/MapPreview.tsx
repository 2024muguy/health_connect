'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { Navigation, ArrowRight } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

const MapContainer = dynamic(() => import('react-leaflet').then((m) => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then((m) => m.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then((m) => m.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then((m) => m.Popup), { ssr: false });

// Ongata Rongai destination
const ONGATA_RONGAI = { lat: -1.3975, lng: 36.7441, name: 'Ongata Rongai' };
const CENTRAL_CLINIC = { lat: -1.2921, lng: 36.8219, name: 'HealthConnect Central' };

export function MapPreview() {
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

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <strong className="text-sm flex items-center gap-2">
          <Navigation size={14} className="text-primary" />
          Directions
        </strong>
        <Link
          href="/clinic#directions"
          className="text-[11px] text-primary hover:underline flex items-center gap-1"
        >
          Full map <ArrowRight size={11} />
        </Link>
      </div>

      <div className="rounded-lg overflow-hidden border border-border" style={{ height: 140 }}>
        <MapContainer
          center={[ONGATA_RONGAI.lat, ONGATA_RONGAI.lng]}
          zoom={11}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={false}
          dragging={false}
          zoomControl={false}
          attributionControl={false}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Marker position={[CENTRAL_CLINIC.lat, CENTRAL_CLINIC.lng]}>
            <Popup>{CENTRAL_CLINIC.name}</Popup>
          </Marker>
          <Marker position={[ONGATA_RONGAI.lat, ONGATA_RONGAI.lng]}>
            <Popup>{ONGATA_RONGAI.name}</Popup>
          </Marker>
        </MapContainer>
      </div>

      <div className="mt-2 text-[11px] text-muted-foreground">
        Destination: <strong className="text-foreground">{ONGATA_RONGAI.name}</strong>
      </div>
    </div>
  );
}
