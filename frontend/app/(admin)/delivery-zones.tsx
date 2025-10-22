import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import MapView, { Polygon } from 'react-native-maps';
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
}

export default function DeliveryZonesScreen() {
  const [zones, setZones] = useState<DeliveryZone[]>([]);
  const [loading, setLoading] = useState(true);

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
        initialRegion={{
          latitude: 37.7749,
          longitude: -122.4194,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
      >
        {zones.map((zone) => (
          <Polygon
            key={zone.id}
            coordinates={zone.coordinates || []}
            strokeColor="#FF9500"
            fillColor="rgba(255, 149, 0, 0.5)"
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