import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  SafeAreaView,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../../utils/axios';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../store/authStore';
import * as Location from 'expo-location';

interface CartItem {
  product_id: string;
  quantity: number;
  product: {
    id: string;
    name: string;
    price: number;
    image: string;
    stock: number;
  };
}

export default function CartScreen() {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [isFetchingLocation, setIsFetchingLocation] = useState(false);
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    fetchCart();
    if (user?.address) {
      setDeliveryAddress(user.address);
    }
  }, []);

  const handleGetCurrentLocation = async () => {
    setIsFetchingLocation(true);
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Permission to access location was denied.');
        setIsFetchingLocation(false);
        return;
      }

      let location = await Location.getCurrentPositionAsync({});
      let address = await Location.reverseGeocodeAsync(location.coords);
      
      if (address.length > 0) {
        const { street, city, region, postalCode, country } = address[0];
        const formattedAddress = `${street}, ${city}, ${region} ${postalCode}, ${country}`;
        setDeliveryAddress(formattedAddress);
      }
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Error', 'Could not fetch your location.');
    } finally {
      setIsFetchingLocation(false);
    }
  };

  const fetchCart = async () => {
    try {
      const response = await apiClient.get('/cart');
      setCartItems(response.data.items);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId: string, newQuantity: number) => {
    if (newQuantity < 1) return;

    try {
      await apiClient.post('/cart/update', {
        product_id: productId,
        quantity: newQuantity,
      });
      fetchCart();
    } catch (error) {
      console.error('Error updating quantity:', error);
      Alert.alert('Error', 'Failed to update quantity');
    }
  };

  const removeItem = async (productId: string) => {
    try {
      await apiClient.post(`/cart/remove/${productId}`);
      fetchCart();
    } catch (error) {
      console.error('Error removing item:', error);
      Alert.alert('Error', 'Failed to remove item');
    }
  };

  const handleCheckout = async () => {
    if (!deliveryAddress.trim()) {
      Alert.alert('Error', 'Please enter a delivery address');
      return;
    }

    if (cartItems.length === 0) {
      Alert.alert('Error', 'Your cart is empty');
      return;
    }

    Alert.alert(
      'Confirm Order',
      `Total: $${calculateTotal().toFixed(2)}\nDelivery to: ${deliveryAddress}`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Place Order',
          onPress: async () => {
            setCheckoutLoading(true);
            try {
              await apiClient.post('/orders', {
                items: cartItems.map((item) => ({
                  product_id: item.product_id,
                  quantity: item.quantity,
                })),
                delivery_address: deliveryAddress,
              });
              Alert.alert('Success', 'Order placed successfully!', [
                { text: 'OK', onPress: () => router.push('/(customer)/orders') },
              ]);
              fetchCart();
            } catch (error: any) {
              console.error('Error placing order:', error);
              Alert.alert('Error', error.response?.data?.detail || 'Failed to place order');
            } finally {
              setCheckoutLoading(false);
            }
          },
        },
      ]
    );
  };

  const calculateTotal = () => {
    return cartItems.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  };

  const renderCartItem = ({ item }: { item: CartItem }) => (
    <View style={styles.cartItem}>
      <Image
        source={{ uri: item.product.image }}
        style={styles.itemImage}
        resizeMode="cover"
      />
      <View style={styles.itemDetails}>
        <Text style={styles.itemName}>{item.product.name}</Text>
        <Text style={styles.itemPrice}>${item.product.price.toFixed(2)}</Text>
        <View style={styles.quantityContainer}>
          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => updateQuantity(item.product_id, item.quantity - 1)}
          >
            <Ionicons name="remove" size={16} color="#007AFF" />
          </TouchableOpacity>
          <Text style={styles.quantity}>{item.quantity}</Text>
          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => updateQuantity(item.product_id, item.quantity + 1)}
            disabled={item.quantity >= item.product.stock}
          >
            <Ionicons name="add" size={16} color="#007AFF" />
          </TouchableOpacity>
        </View>
      </View>
      <TouchableOpacity
        style={styles.removeButton}
        onPress={() => removeItem(item.product_id)}
      >
        <Ionicons name="trash-outline" size={20} color="#ff3b30" />
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Cart</Text>
      </View>

      {cartItems.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="cart-outline" size={80} color="#ccc" />
          <Text style={styles.emptyText}>Your cart is empty</Text>
          <TouchableOpacity
            style={styles.shopButton}
            onPress={() => router.push('/(customer)/home')}
          >
            <Text style={styles.shopButtonText}>Start Shopping</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          <FlatList
            data={cartItems}
            renderItem={renderCartItem}
            keyExtractor={(item) => item.product_id}
            contentContainerStyle={styles.cartList}
          />

          <View style={styles.checkoutContainer}>
            <View style={styles.addressContainer}>
              <Text style={styles.addressLabel}>Delivery Address</Text>
              <TextInput
                style={styles.addressInput}
                value={deliveryAddress}
                onChangeText={setDeliveryAddress}
                placeholder="Enter your delivery address"
              />
              <TouchableOpacity style={styles.locationButton} onPress={handleGetCurrentLocation} disabled={isFetchingLocation}>
                {isFetchingLocation ? (
                  <ActivityIndicator size="small" color="#007AFF" />
                ) : (
                  <>
                    <Ionicons name="location-sharp" size={16} color="#007AFF" />
                    <Text style={styles.locationButtonText}>Use My Current Location</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
            <View style={styles.totalContainer}>
              <Text style={styles.totalText}>Total:</Text>
              <Text style={styles.totalAmount}>${calculateTotal().toFixed(2)}</Text>
            </View>

            <TouchableOpacity
              style={[styles.checkoutButton, checkoutLoading && styles.checkoutButtonDisabled]}
              onPress={handleCheckout}
              disabled={checkoutLoading}
            >
              <Text style={styles.checkoutButtonText}>
                {checkoutLoading ? 'Processing...' : 'Place Order'}
              </Text>
            </TouchableOpacity>
          </View>
        </>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  cartList: {
    paddingVertical: 8,
  },
  cartItem: {
    flexDirection: 'row',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  itemImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  itemDetails: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'space-between',
  },
  itemName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  itemPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  quantityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  quantityButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  quantity: {
    fontSize: 16,
    fontWeight: '600',
    minWidth: 24,
    textAlign: 'center',
  },
  removeButton: {
    padding: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginTop: 16,
    marginBottom: 24,
  },
  shopButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
  },
  shopButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  checkoutContainer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    backgroundColor: '#fff',
  },
  addressContainer: {
    marginBottom: 16,
  },
  addressLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  addressInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 8,
  },
  locationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
    borderRadius: 8,
    backgroundColor: '#eef',
  },
  locationButtonText: {
    color: '#007AFF',
    marginLeft: 8,
    fontWeight: '600',
  },
  totalContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  totalText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  totalAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  checkoutButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  checkoutButtonDisabled: {
    opacity: 0.6,
  },
  checkoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
