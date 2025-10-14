import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  TextInput,
  RefreshControl,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../../utils/axios';
import { useAuthStore } from '../../store/authStore';

interface Product {
  id: string;
  name: string;
  brand: string;
  description: string;
  price: number;
  category: string;
  stock: number;
  unit: string;
  variant: string;
  code: string | null;
  barcode: string | null;
  image: string;
}

const categoryData = [
  { name: 'all', icon: 'apps-outline' as const },
  { name: 'drinks', icon: 'cafe-outline' as const },
  { name: 'enterprise', icon: 'briefcase-outline' as const },
  { name: 'snacks', icon: 'fast-food-outline' as const },
  { name: 'sweets', icon: 'ice-cream-outline' as const },
  { name: 'oil', icon: 'water-outline' as const },
  { name: 'dairy products', icon: 'egg-outline' as const },
];

export default function HomeScreen() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [page, setPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const user = useAuthStore((state) => state.user);
  
  // Debounced search query for API calls
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');

  // Filter products based on search query (for immediate UI feedback)
  const filteredProducts = products.filter((product) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      product.name.toLowerCase().includes(query) ||
      product.description.toLowerCase().includes(query) ||
      product.brand.toLowerCase().includes(query)
    );
  });
  
  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 500); // 500ms delay

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    fetchProducts(true);
  }, []);

  useEffect(() => {
    // When category changes, reset products and fetch from page 1
    if (!loading) { // Avoid fetching on initial mount
      fetchProducts(true);
    }
  }, [selectedCategory]);
  
  useEffect(() => {
    // When debounced search query changes, reset products and fetch from page 1
    if (!loading) { // Avoid fetching on initial mount
      fetchProducts(true);
    }
  }, [debouncedSearchQuery]);

  const fetchProducts = async (reset = false) => {
    if (loadingMore) return;

    const currentPage = reset ? 1 : page;
    
    // Don't fetch if we've already loaded all products
    if (!reset && products.length >= totalProducts) {
      return;
    }

    if (reset) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }

    try {
      const params = {
        page: currentPage,
        limit: 20,
        category: selectedCategory !== 'all' ? selectedCategory : undefined,
        query: debouncedSearchQuery || undefined, // Use debounced search query
      };
      
      // Use the new search endpoint
      const endpoint = debouncedSearchQuery ? '/api/v1/products/search' : '/api/v1/products';
      const response = await apiClient.get(endpoint, { params });
      
      const newProducts = response.data.products || [];
      setProducts(prev => reset ? newProducts : [...prev, ...newProducts]);
      setTotalProducts(response.data.total || 0);
      setPage(currentPage + 1);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  };

  const addToCart = async (productId: string) => {
    try {
      await apiClient.post('/cart/add', {
        product_id: productId,
        quantity: 1,
      });
      alert('Added to cart!');
    } catch (error) {
      console.error('Error adding to cart:', error);
      alert('Failed to add to cart');
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    setPage(1);
    fetchProducts(true);
  };

  const renderProduct = ({ item }: { item: Product }) => (
    <TouchableOpacity
      style={styles.productCard}
      onPress={() => setSelectedProduct(item)}
      activeOpacity={0.7}
    >
      <View style={styles.imageContainer}>
        <Image
          source={{ uri: item.image }}
          style={styles.productImage}
          resizeMode="cover"
        />
        {item.stock < 10 && item.stock > 0 && (
          <View style={styles.lowStockBadge}>
            <Text style={styles.lowStockText}>Low Stock</Text>
          </View>
        )}
        {item.stock === 0 && (
          <View style={styles.outOfStockBadge}>
            <Text style={styles.outOfStockText}>Out of Stock</Text>
          </View>
        )}
      </View>
      <View style={styles.productInfo}>
        <Text style={styles.productName} numberOfLines={1}>
          {item.name}
        </Text>
        <Text style={styles.productDescription} numberOfLines={2}>
          {item.description}
        </Text>
        <View style={styles.productFooter}>
          <View>
            <Text style={styles.productPrice}>₹{item.price.toFixed(2)}</Text>
            <Text style={styles.productStock}>
              {item.stock > 0 ? `${item.stock} in stock` : 'Out of stock'}
            </Text>
          </View>
          <TouchableOpacity
            style={[styles.addButton, item.stock === 0 && styles.addButtonDisabled]}
            onPress={(e) => {
              e.stopPropagation();
              addToCart(item.id);
            }}
            disabled={item.stock === 0}
            activeOpacity={0.7}
          >
            <Ionicons name="add" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
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
      {/* Product Details Modal */}
      {selectedProduct && (
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setSelectedProduct(null)}
        >
          <View style={styles.modalContent} onStartShouldSetResponder={() => true}>
            <View style={styles.modalImageContainer}>
              <Image
                source={{ uri: selectedProduct.image }}
                style={styles.modalImage}
                resizeMode="cover"
              />
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setSelectedProduct(null)}
              >
                <Ionicons name="close" size={24} color="#fff" />
              </TouchableOpacity>
            </View>
            <View style={styles.modalDetails}>
              <Text style={styles.modalTitle}>{selectedProduct.name}</Text>
              <Text style={styles.modalBrand}>{selectedProduct.brand}</Text>
              <Text style={styles.modalPrice}>₹{selectedProduct.price.toFixed(2)}</Text>
              <Text style={styles.modalStock}>
                {selectedProduct.stock > 0
                  ? `${selectedProduct.stock} ${selectedProduct.unit} in stock`
                  : 'Out of stock'}
              </Text>
              <Text style={styles.modalVariant}>
                Variant: {selectedProduct.variant}
              </Text>
              <Text style={styles.modalDescription}>{selectedProduct.description}</Text>
              {selectedProduct.code && (
                <Text style={styles.modalCode}>Product Code: {selectedProduct.code}</Text>
              )}
              {selectedProduct.barcode && (
                <Text style={styles.modalCode}>Barcode: {selectedProduct.barcode}</Text>
              )}
              <TouchableOpacity
                style={[
                  styles.modalAddButton,
                  selectedProduct.stock === 0 && styles.addButtonDisabled,
                ]}
                onPress={() => {
                  addToCart(selectedProduct.id);
                  setSelectedProduct(null);
                }}
                disabled={selectedProduct.stock === 0}
              >
                <Text style={styles.modalAddButtonText}>Add to Cart</Text>
              </TouchableOpacity>
            </View>
          </View>
        </TouchableOpacity>
      )}

      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hi, {user?.name?.split(' ')[0]}! 👋</Text>
          <Text style={styles.headerSubtitle}>What are you looking for?</Text>
        </View>
      </View>

      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#999" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search products..."
          placeholderTextColor="#999"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      <View style={styles.categoriesContainer}>
        <FlatList
          horizontal
          showsHorizontalScrollIndicator={false}
          data={categoryData}
          keyExtractor={(item) => item.name}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.categoryChip,
                selectedCategory === item.name && styles.categoryChipActive,
              ]}
              onPress={() => setSelectedCategory(item.name)}
              activeOpacity={0.7}
            >
              <Ionicons
                name={item.icon}
                size={20}
                color={selectedCategory === item.name ? '#fff' : '#666'}
                style={styles.categoryIcon}
              />
              <Text
                style={[
                  styles.categoryChipText,
                  selectedCategory === item.name && styles.categoryChipTextActive,
                ]}
              >
                {item.name.charAt(0).toUpperCase() + item.name.slice(1)}
              </Text>
            </TouchableOpacity>
          )}
        />
      </View>

      <FlatList
        data={filteredProducts}
        renderItem={renderProduct}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.productList}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        onEndReached={() => !searchQuery && fetchProducts()} // Only load more if not searching
        onEndReachedThreshold={0.5}
        ListFooterComponent={loadingMore && !searchQuery ? <ActivityIndicator size="large" color="#007AFF" style={{ marginVertical: 20 }} /> : null}
        ListEmptyComponent={
          !loading && (
            <View style={styles.emptyContainer}>
              <Ionicons name="cube-outline" size={64} color="#ccc" />
              <Text style={styles.emptyText}>
                {searchQuery ? `No products found for "${searchQuery}"` : 'No products found'}
              </Text>
            </View>
          )
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    zIndex: 1000,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 20,
    width: '90%',
    maxHeight: '90%',
    overflow: 'hidden',
  },
  modalImageContainer: {
    width: '100%',
    height: 300,
    position: 'relative',
  },
  modalImage: {
    width: '100%',
    height: '100%',
  },
  closeButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalDetails: {
    padding: 20,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  modalBrand: {
    fontSize: 16,
    color: '#666',
    marginBottom: 12,
  },
  modalPrice: {
    fontSize: 28,
    fontWeight: '700',
    color: '#007AFF',
    marginBottom: 8,
  },
  modalStock: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  modalVariant: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  modalDescription: {
    fontSize: 14,
    color: '#444',
    lineHeight: 20,
    marginBottom: 16,
  },
  modalCode: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  modalAddButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  modalAddButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    backgroundColor: '#fff',
  },
  greeting: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a1a1a',
  },
  headerSubtitle: {
    fontSize: 15,
    color: '#666',
    marginTop: 4,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 20,
    marginTop: 20,
    marginBottom: 16,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
    borderRadius: 16,
    height: 50,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 15,
    color: '#1a1a1a',
  },
  categoriesContainer: {
    paddingLeft: 20,
    marginBottom: 16,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#fff',
    marginRight: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  categoryChipActive: {
    backgroundColor: '#007AFF',
  },
  categoryChipText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  categoryChipTextActive: {
    color: '#fff',
  },
  categoryIcon: {
    marginRight: 8,
  },
  productList: {
    paddingHorizontal: 12,
    paddingBottom: 20,
  },
  productCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 20,
    margin: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
    maxWidth: '48%',
    overflow: 'hidden',
  },
  imageContainer: {
    position: 'relative',
  },
  productImage: {
    width: '100%',
    height: 160,
    backgroundColor: '#f0f0f0',
  },
  lowStockBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#FF9500',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  lowStockText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
  outOfStockBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#FF3B30',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  outOfStockText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
  productInfo: {
    padding: 14,
  },
  productName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  productDescription: {
    fontSize: 12,
    color: '#999',
    lineHeight: 16,
    marginBottom: 12,
  },
  productFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  productPrice: {
    fontSize: 20,
    fontWeight: '700',
    color: '#007AFF',
  },
  productStock: {
    fontSize: 11,
    color: '#999',
    marginTop: 2,
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  addButtonDisabled: {
    backgroundColor: '#ccc',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginTop: 16,
  },
});