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
import { format } from 'date-fns';
import { Picker } from '@react-native-picker/picker';

interface Order {
  id: string;
  user_name: string;
  user_phone: string;
  user_address: string;
  items: Array<{
    product_name: string;
    quantity: number;
    price: number;
  }>;
  total_amount: number;
  status: string;
  delivery_agent_id: string | null;
  created_at: string;
}

const statusOptions = [
  { label: 'Pending', value: 'pending' },
  { label: 'Confirmed', value: 'confirmed' },
  { label: 'Preparing', value: 'preparing' },
  { label: 'Out for Delivery', value: 'out_for_delivery' },
  { label: 'Delivered', value: 'delivered' },
  { label: 'Cancelled', value: 'cancelled' },
];

const statusColors: Record<string, string> = {
  pending: '#FFA500',
  confirmed: '#4CAF50',
  preparing: '#2196F3',
  out_for_delivery: '#9C27B0',
  delivered: '#4CAF50',
  cancelled: '#F44336',
};

export default function OrdersScreen() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedOrder, setExpandedOrder] = useState<string | null>(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await apiClient.get('/api/orders');
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchOrders();
  };

  const updateOrderStatus = async (orderId: string, newStatus: string) => {
    try {
      await apiClient.put(`/api/orders/${orderId}/status`, {
        status: newStatus,
      });
      Alert.alert('Success', 'Order status updated');
      fetchOrders();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update order');
    }
  };

  const renderOrder = ({ item }: { item: Order }) => {
    const isExpanded = expandedOrder === item.id;

    return (
      <TouchableOpacity
        style={styles.orderCard}
        onPress={() => setExpandedOrder(isExpanded ? null : item.id)}
        activeOpacity={0.7}
      >
        <View style={styles.orderHeader}>
          <View>
            <Text style={styles.orderId}>#{item.id.slice(0, 8)}</Text>
            <Text style={styles.customerName}>{item.user_name}</Text>
            <Text style={styles.orderDate}>
              {format(new Date(item.created_at), 'MMM dd, yyyy HH:mm')}
            </Text>
          </View>
          <View>
            <Text style={styles.amount}>${item.total_amount.toFixed(2)}</Text>
            <View
              style={[
                styles.statusBadge,
                { backgroundColor: statusColors[item.status] || '#999' },
              ]}
            >
              <Text style={styles.statusText}>
                {item.status.replace('_', ' ').toUpperCase()}
              </Text>
            </View>
          </View>
        </View>

        {isExpanded && (
          <View style={styles.expandedContent}>
            <View style={styles.detailRow}>
              <Ionicons name="call" size={16} color="#666" />
              <Text style={styles.detailText}>{item.user_phone}</Text>
            </View>
            <View style={styles.detailRow}>
              <Ionicons name="location" size={16} color="#666" />
              <Text style={styles.detailText}>{item.user_address}</Text>
            </View>

            <View style={styles.itemsSection}>
              <Text style={styles.sectionTitle}>Items:</Text>
              {item.items.map((orderItem, index) => (
                <View key={index} style={styles.orderItem}>
                  <Text style={styles.itemName}>
                    {orderItem.quantity}x {orderItem.product_name}
                  </Text>
                  <Text style={styles.itemPrice}>
                    ${(orderItem.price * orderItem.quantity).toFixed(2)}
                  </Text>
                </View>
              ))}
            </View>

            <View style={styles.statusSection}>
              <Text style={styles.sectionTitle}>Update Status:</Text>
              <View style={styles.pickerContainer}>
                <Picker
                  selectedValue={item.status}
                  onValueChange={(value) => updateOrderStatus(item.id, value)}
                  style={styles.picker}
                >
                  {statusOptions.map((option) => (
                    <Picker.Item
                      key={option.value}
                      label={option.label}
                      value={option.value}
                    />
                  ))}
                </Picker>
              </View>
            </View>

            {item.delivery_agent_id && (
              <View style={styles.agentInfo}>
                <Ionicons name="bicycle" size={16} color="#34C759" />
                <Text style={styles.agentText}>
                  Agent: {item.delivery_agent_id.slice(0, 8)}
                </Text>
              </View>
            )}
          </View>
        )}

        <View style={styles.expandIcon}>
          <Ionicons
            name={isExpanded ? 'chevron-up' : 'chevron-down'}
            size={20}
            color="#666"
          />
        </View>
      </TouchableOpacity>
    );
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
      <View style={styles.header}>
        <Text style={styles.headerTitle}>All Orders</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Ionicons name="refresh" size={24} color="#FF9500" />
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
            <Ionicons name="receipt-outline" size={80} color="#ccc" />
            <Text style={styles.emptyText}>No orders yet</Text>
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
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  orderId: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  customerName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  orderDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  amount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FF9500',
    textAlign: 'right',
    marginBottom: 4,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-end',
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#fff',
  },
  expandedContent: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  detailText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  itemsSection: {
    marginTop: 12,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  itemName: {
    fontSize: 14,
    color: '#333',
  },
  itemPrice: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF9500',
  },
  statusSection: {
    marginTop: 16,
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    backgroundColor: '#f9f9f9',
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  agentInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  agentText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#34C759',
    fontWeight: '500',
  },
  expandIcon: {
    alignItems: 'center',
    marginTop: 8,
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
