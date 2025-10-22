import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import MapView, { Polygon, Region } from 'react-native-maps';
import apiClient from '../../utils/axios';
import { SafeAreaView } from 'react-native-safe-area-context';

interface GeoJSONPolygon {
  type: string;
  coordinates: number[][][]; // [longitude, latitude] pairs
}

interface DeliveryZone {
  id: string;
  name: string;
  geometry: GeoJSONPolygon;
  coordinates?: Array<{ latitude: number; longitude: number }>;
}

export default function DeliveryZonesScreen() {
  const [zones, setZones] = useState<DeliveryZone[]>([]);
  const [loading, setLoading] = useState(true);
  const [initialRegion, setInitialRegion] = useState<Region | undefined>(undefined);

  useEffect(() => {
    fetchDeliveryZones();
  }, []);

  const fetchDeliveryZones = async () => {
    try {
      const response = await apiClient.get('/delivery-zones');
      
      // Convert GeoJSON format to react-native-maps format
      const convertedZones = response.data.map((zone: any) => {
        // Handle both new GeoJSON format and legacy format
        if (zone.geometry && zone.geometry.coordinates) {
          // New GeoJSON format
          const coordinates = zone.geometry.coordinates[0].map((coord: number[]) => ({
            longitude: coord[0],
            latitude: coord[1]
          }));
          return {
            ...zone,
            coordinates: coordinates
          };
        } else if (zone.coordinates) {
          // Legacy format
          return zone;
        }
        return zone;
      });
      
      setZones(convertedZones);
      
      // Set initial region to center of first zone if available
      if (convertedZones.length > 0 && convertedZones[0].coordinates && convertedZones[0].coordinates.length > 0) {
        const coords = convertedZones[0].coordinates;
        const latitudes = coords.map(c => c.latitude);
        const longitudes = coords.map(c => c.longitude);
        
        const minLat = Math.min(...latitudes);
        const maxLat = Math.max(...latitudes);
        const minLng = Math.min(...longitudes);
        const maxLng = Math.max(...longitudes);
        
        setInitialRegion({
          latitude: (minLat + maxLat) / 2,
          longitude: (minLng + maxLng) / 2,
          latitudeDelta: (maxLat - minLat) * 1.2,
          longitudeDelta: (maxLng - minLng) * 1.2,
        });
      }
    } catch (error) {
      console.error('Error fetching delivery zones:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF9500" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={initialRegion || {
          latitude: 13.105616358890572, // Bangalore latitude
          longitude: 77.59514283308448, // Bangalore longitude
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
      >
        {zones.map((zone) => (
          <Polygon
            key={zone.id}
            coordinates={zone.coordinates || []}
            strokeColor="#FF9500"
            fillColor="rgba(235, 164, 65, 0.5)"
            strokeWidth={2}
          />
        ))}
      </MapView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    ...StyleSheet.absoluteFillObject,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});