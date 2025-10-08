import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';
import * as Location from 'expo-location';
import apiClient from '../../utils/axios';
import { useLocalSearchParams } from 'expo-router';
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
  delivery_agent_id?: string;
}

interface AgentLocation {
  latitude: number;
  longitude: number;
}

export default function CustomerOrderMapScreen() {
  const { orderId } = useLocalSearchParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [deliveryLocation, setDeliveryLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [agentLocation, setAgentLocation] = useState<AgentLocation | null>(null);
  const [routeCoordinates, setRouteCoordinates] = useState<Array<{ latitude: number; longitude: number }>>([]);

  useEffect(() => {
    if (orderId) {
      fetchOrderDetails(orderId as string);
    }
  }, [orderId]);

  const fetchOrderDetails = async (id: string) => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Permission to access location was denied.');
        setLoading(false);
        return;
      }

      const response = await apiClient.get(`/orders/${id}`);
      const fetchedOrder: Order = response.data;
      setOrder(fetchedOrder);

      // Get delivery location coordinates
      if (fetchedOrder.delivery_location) {
        setDeliveryLocation(fetchedOrder.delivery_location);
      } else {
        const geocodedLocation = await Location.geocodeAsync(fetchedOrder.user_address);
        if (geocodedLocation.length > 0) {
          setDeliveryLocation({ latitude: geocodedLocation[0].latitude, longitude: geocodedLocation[0].longitude });
        }
      }

      // Fetch agent location if order is out for delivery (conceptual)
      // In a real app, you'd have a backend endpoint to get the agent's real-time location.
      // For now, we'll simulate or use a static location if available.
      if (fetchedOrder.status === 'out_for_delivery' && fetchedOrder.delivery_agent_id) {
        // Example: Fetch agent's last known location from backend
        // const agentLocResponse = await apiClient.get(`/agents/${fetchedOrder.delivery_agent_id}/location`);
        // setAgentLocation(agentLocResponse.data);
        // For now, let's assume agent is near the delivery location for simulation
        if (fetchedOrder.delivery_location) {
          setAgentLocation({
            latitude: fetchedOrder.delivery_location.latitude + 0.005,
            longitude: fetchedOrder.delivery_location.longitude + 0.005,
          });
        }
      }

      // Fetch route if both agent and delivery locations are available
      if (agentLocation && deliveryLocation) {
        try {
          const waypoints = [
            { latitude: agentLocation.latitude, longitude: agentLocation.longitude },
            { latitude: deliveryLocation.latitude, longitude: deliveryLocation.longitude },
          ];
          const routeResponse = await apiClient.post('/route/optimize', waypoints);
          if (routeResponse.data && routeResponse.data.route) {
            setRouteCoordinates(routeResponse.data.route);
          }
        } catch (routingError) {
          console.error('Error fetching customer route:', routingError);
          // Fallback to straight line
          setRouteCoordinates([
            { latitude: agentLocation.latitude, longitude: agentLocation.longitude },
            { latitude: deliveryLocation.latitude, longitude: deliveryLocation.longitude },
          ]);
        }
      }

    } catch (error) {
      console.error('Error fetching order details:', error);
      Alert.alert('Error', 'Failed to load order details.');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !order || !deliveryLocation) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF9500" />
        <Text style={styles.loadingText}>Loading order details and map...</Text>
      </View>
    );
  }

  const initialRegion = {
    latitude: deliveryLocation.latitude,
    longitude: deliveryLocation.longitude,
    latitudeDelta: LATITUDE_DELTA,
    longitudeDelta: LONGITUDE_DELTA,
  };

  return (
    <SafeAreaView style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={initialRegion}
      >
        {deliveryLocation && (
          <Marker
            coordinate={deliveryLocation}
            title="Delivery Location"
            description={order.user_address}
            pinColor="red"
          />
        )}
        {agentLocation && (
          <Marker
            coordinate={agentLocation}
            title="Delivery Agent"
            pinColor="blue"
          />
        )}
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
});
