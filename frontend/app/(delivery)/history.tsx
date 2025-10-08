import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../../utils/axios';
import { useAuthStore } from '../../store/authStore';
import { format } from 'date-fns';

interface Order {
  id: string;
  user_name: string;
  total_amount: number;
  status: string;
  created_at: string;
}

export default function DeliveryHistoryScreen() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await apiClient.get('/orders');
      const deliveredOrders = response.data.filter(
        (order: Order) =>
          order.delivery_agent_id === user?.id &&
          ['delivered', 'cancelled'].includes(order.status)
      );
      setOrders(deliveredOrders);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchHistory();
  };

  const renderOrder = ({ item }: { item: Order }) => (
    <View style={styles.orderCard}>
      <View style={styles.orderHeader}>
        <View>
          <Text style={styles.customerName}>{item.user_name}</Text>
          <Text style={styles.orderDate}>
            {format(new Date(item.created_at), 'MMM dd, yyyy HH:mm')}
          </Text>
        </View>
        <Text style={styles.amount}>${item.total_amount.toFixed(2)}</Text>
      </View>
      <View
        style={[
          styles.statusBadge,
          { backgroundColor: item.status === 'delivered' ? '#34C759' : '#FF3B30' },
        ]}
      >
        <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#34C759" />
      </View>
    );
  }

  const totalEarnings = orders
    .filter((o) => o.status === 'delivered')
    .reduce((sum, o) => sum + o.total_amount * 0.1, 0); // 10% commission

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Delivery History</Text>
      </View>

      <View style={styles.statsCard}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{orders.filter((o) => o.status === 'delivered').length}</Text>
          <Text style={styles.statLabel}>Completed</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statValue}>${totalEarnings.toFixed(2)}</Text>
          <Text style={styles.statLabel}>Earnings</Text>
        </View>
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
            <Ionicons name="time-outline" size={80} color="#ccc" />
            <Text style={styles.emptyText}>No delivery history</Text>
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
  statsCard: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    margin: 16,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#34C759',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  statDivider: {
    width: 1,
    backgroundColor: '#f0f0f0',
    marginHorizontal: 16,
  },
  ordersList: {
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  orderCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  customerName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  orderDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  amount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#34C759',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  statusText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#fff',
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
