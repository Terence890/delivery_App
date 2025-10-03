import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  SafeAreaView,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../../utils/axios';
import { useAuthStore } from '../../store/authStore';
import { format } from 'date-fns';

interface Order {
  id: string;
  user_name: string;
  user_phone: string;
  user_address: string;
  items: Array<{
    product_name: string;
    quantity: number;
  }>;
  total_amount: number;
  status: string;
  delivery_agent_id: string;
  created_at: string;
}

export default function ActiveDeliveriesScreen() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    fetchActiveOrders();
  }, []);

  const fetchActiveOrders = async () => {
    try {
      const response = await apiClient.get('/api/orders');
      const activeOrders = response.data.filter(
        (order: Order) =>
          order.delivery_agent_id === user?.id &&
          ['preparing', 'out_for_delivery'].includes(order.status)
      );
      setOrders(activeOrders);
    } catch (error) {
      console.error('Error fetching active orders:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchActiveOrders();
  };

  const updateOrderStatus = async (orderId: string, newStatus: string) => {
    try {
      await apiClient.put(`/api/orders/${orderId}/status`, {
        status: newStatus,
      });
      Alert.alert('Success', `Order marked as ${newStatus.replace('_', ' ')}`);
      fetchActiveOrders();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update order');
    }
  };

  const renderOrder = ({ item }: { item: Order }) => {
    const isOutForDelivery = item.status === 'out_for_delivery';

    return (
      <View style={styles.orderCard}>
        <View style={styles.statusBadge}>
          <Ionicons
            name={isOutForDelivery ? 'car' : 'restaurant'}
            size={16}
            color="#fff"
          />
          <Text style={styles.statusText}>
            {item.status.replace('_', ' ').toUpperCase()}
          </Text>
        </View>

        <View style={styles.orderHeader}>
          <Text style={styles.customerName}>{item.user_name}</Text>
          <Text style={styles.amount}>${item.total_amount.toFixed(2)}</Text>
        </View>

        <View style={styles.infoRow}>
          <Ionicons name="call" size={16} color="#007AFF" />
          <Text style={styles.phone}>{item.user_phone}</Text>
        </View>

        <View style={styles.infoRow}>
          <Ionicons name="location" size={16} color="#FF3B30" />
          <Text style={styles.address} numberOfLines={2}>
            {item.user_address}
          </Text>
        </View>

        <View style={styles.itemsContainer}>
          <Text style={styles.itemsLabel}>{item.items.length} items</Text>
          {item.items.slice(0, 2).map((orderItem, index) => (
            <Text key={index} style={styles.itemText}>
              • {orderItem.quantity}x {orderItem.product_name}
            </Text>
          ))}
        </View>

        <View style={styles.actions}>
          {item.status === 'preparing' && (
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => updateOrderStatus(item.id, 'out_for_delivery')}
            >
              <Ionicons name="car" size={20} color="#fff" />
              <Text style={styles.actionButtonText}>Start Delivery</Text>
            </TouchableOpacity>
          )}
          {item.status === 'out_for_delivery' && (
            <TouchableOpacity
              style={[styles.actionButton, styles.deliveredButton]}
              onPress={() => updateOrderStatus(item.id, 'delivered')}
            >
              <Ionicons name="checkmark-done" size={20} color="#fff" />
              <Text style={styles.actionButtonText}>Mark Delivered</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#34C759" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Active Deliveries</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Ionicons name="refresh" size={24} color="#34C759" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={orders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.ordersList}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="bicycle-outline" size={80} color="#ccc" />
            <Text style={styles.emptyText}>No active deliveries</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  ordersList: {
    padding: 16,
  },
  orderCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FF9500',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    alignSelf: 'flex-start',
    marginBottom: 12,
    gap: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#fff',
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  customerName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  amount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#34C759',
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  phone: {
    fontSize: 14,
    color: '#007AFF',
    marginLeft: 8,
    fontWeight: '500',
  },
  address: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
  },
  itemsContainer: {
    marginVertical: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  itemsLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    marginBottom: 4,
  },
  itemText: {
    fontSize: 13,
    color: '#333',
    marginTop: 2,
  },
  actions: {
    marginTop: 12,
  },
  actionButton: {
    flexDirection: 'row',
    backgroundColor: '#FF9500',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  deliveredButton: {
    backgroundColor: '#34C759',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginTop: 16,
  },
});
