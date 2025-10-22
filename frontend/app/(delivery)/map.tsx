import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Dimensions,
  ScrollView,
} from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';
import * as Location from 'expo-location';
import apiClient from '../../utils/axios';
import { useAuthStore } from '../../store/authStore';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width, height } = Dimensions.get('window');
const ASPECT_RATIO = width / height;
const LATITUDE_DELTA = 0.0922;
const LONGITUDE_DELTA = LATITUDE_DELTA * ASPECT_RATIO;

interface Order {
  id: string;
  user_name: string;
  user_address: string;
  delivery_location?: { latitude: number; longitude: number };
  status: string;
  estimated_delivery_time?: { minutes: number; formatted: string };
}

export default function DeliveryMapScreen() {
  const [driverLocation, setDriverLocation] = useState<Location.LocationObjectCoords | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [routeCoordinates, setRouteCoordinates] = useState<Array<{ latitude: number; longitude: number }>>([]);
  const [estimatedDeliveryTimes, setEstimatedDeliveryTimes] = useState<Array<{ orderId: string; time: string }>>([]);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Permission to access location was denied.');
        setLoading(false);
        return;
      }

      let location = await Location.getCurrentPositionAsync({});
      setDriverLocation(location.coords);
      fetchActiveOrders(location.coords);
    })();
  }, []);

  const fetchActiveOrders = async (currentCoords: Location.LocationObjectCoords) => {
    try {
      const response = await apiClient.get('/orders');
      const activeOrders = response.data.filter(
        (order: Order) =>
          order.delivery_agent_id === user?.id &&
          ['preparing', 'out_for_delivery'].includes(order.status)
      );
      setOrders(activeOrders);

      // Get coordinates for all active orders
      const destinationCoords = await Promise.all(
        activeOrders.map(async (order: Order) => {
          if (order.delivery_location) {
            return order.delivery_location;
          } else {
            // Reverse geocode address to get coordinates if not already present
            const geocodedLocation = await Location.geocodeAsync(order.user_address);
            if (geocodedLocation.length > 0) {
              return { latitude: geocodedLocation[0].latitude, longitude: geocodedLocation[0].longitude };
            }
            return null;
          }
        })
      );

      const validDestinationCoords = destinationCoords.filter(Boolean) as Array<{ latitude: number; longitude: number }>;
      const validOrders = activeOrders.filter((order: Order) => order.delivery_location) as Order[];

      if (validDestinationCoords.length > 0 && currentCoords) {
        const waypoints = [
          { latitude: currentCoords.latitude, longitude: currentCoords.longitude },
          ...validDestinationCoords,
        ];

        try {
          // Use the new optimize-with-eta endpoint for detailed information
          const routeResponse = await apiClient.post('/route/optimize-with-eta', waypoints);
          if (routeResponse.data && routeResponse.data.route) {
            setRouteCoordinates(routeResponse.data.route);
            
            // Extract estimated delivery times for each order
            if (routeResponse.data.waypoint_etas) {
              const etas = routeResponse.data.waypoint_etas
                .slice(1) // Skip the first waypoint (driver's location)
                .map((eta: any, index: number) => ({
                  orderId: validOrders[index]?.id || '',
                  time: eta.eta ? new Date(eta.eta).toLocaleTimeString() : 'N/A'
                }))
                .filter((eta: any) => eta.orderId);
              setEstimatedDeliveryTimes(etas);
            }
          } else {
            Alert.alert('Routing Error', 'Could not get an optimized route.');
            // Fallback to straight lines if routing fails
            setRouteCoordinates([
              { latitude: currentCoords.latitude, longitude: currentCoords.longitude },
              ...validDestinationCoords,
            ]);
          }
        } catch (routingError) {
          console.error('Error calling routing API:', routingError);
          Alert.alert('Routing Error', 'Failed to get optimized route from server.');
          // Fallback to straight lines if routing API call fails
          setRouteCoordinates([
            { latitude: currentCoords.latitude, longitude: currentCoords.longitude },
            ...validDestinationCoords,
          ]);
        }
      } else if (currentCoords) {
        // If no active orders, just show driver's location
        setRouteCoordinates([
          { latitude: currentCoords.latitude, longitude: currentCoords.longitude },
        ]);
      }
    } catch (error) {
      console.error('Error fetching orders or routing:', error);
      Alert.alert('Error', 'Failed to load map data.');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !driverLocation) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#34C759" />
        <Text style={styles.loadingText}>Loading map and orders...</Text>
      </View>
    );
  }

  const initialRegion = {
    latitude: driverLocation.latitude,
    longitude: driverLocation.longitude,
    latitudeDelta: LATITUDE_DELTA,
    longitudeDelta: LONGITUDE_DELTA,
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Estimated Delivery Times Panel */}
      {estimatedDeliveryTimes.length > 0 && (
        <View style={styles.etaPanel}>
          <Text style={styles.etaPanelTitle}>Estimated Delivery Times</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {estimatedDeliveryTimes.map((eta, index) => (
              <View key={eta.orderId} style={styles.etaItem}>
                <Text style={styles.etaOrder}>Order {index + 1}</Text>
                <Text style={styles.etaTime}>{eta.time}</Text>
              </View>
            ))}
          </ScrollView>
        </View>
      )}
      
      <MapView
        style={styles.map}
        initialRegion={initialRegion}
        showsUserLocation
        followsUserLocation
      >
        {driverLocation && (
          <Marker
            coordinate={{ latitude: driverLocation.latitude, longitude: driverLocation.longitude }}
            title="My Location"
            pinColor="blue"
          />
        )}
        {orders.map((order) => order.delivery_location && (
          <Marker
            key={order.id}
            coordinate={order.delivery_location}
            title={order.user_name}
            description={order.user_address}
            pinColor="red"
          />
        ))}
        {routeCoordinates.length > 1 && (
          <Polyline
            coordinates={routeCoordinates}
            strokeWidth={4}
            strokeColor="#007AFF"
          />
        )}
      </MapView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width: width,
    height: height,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  etaPanel: {
    backgroundColor: '#fff',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  etaPanelTitle: {
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  etaItem: {
    backgroundColor: '#f0f0f0',
    padding: 8,
    borderRadius: 8,
    marginRight: 10,
    minWidth: 80,
    alignItems: 'center',
  },
  etaOrder: {
    fontSize: 12,
    color: '#666',
  },
  etaTime: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#007AFF',
  },
});