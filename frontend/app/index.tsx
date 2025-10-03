import React, { useEffect } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useAuthStore } from '../store/authStore';
import { useRouter } from 'expo-router';

export default function Index() {
  const { isAuthenticated, isLoading, user } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    console.log('Index - isLoading:', isLoading, 'isAuthenticated:', isAuthenticated, 'user:', user);
    
    if (!isLoading) {
      if (isAuthenticated && user) {
        console.log('User role:', user.role);
        // Route based on user role
        switch (user.role) {
          case 'customer':
            console.log('Navigating to customer home...');
            router.replace('/(customer)/home');
            break;
          case 'delivery_agent':
            console.log('Navigating to delivery orders...');
            router.replace('/(delivery)/orders');
            break;
          case 'admin':
            console.log('Navigating to admin dashboard...');
            router.replace('/(admin)/dashboard');
            break;
          default:
            console.log('Unknown role, redirecting to login');
            router.replace('/login');
        }
      } else {
        console.log('Not authenticated, redirecting to login');
        router.replace('/login');
      }
    }
  }, [isAuthenticated, isLoading, user]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#007AFF" />
      <Text style={styles.text}>Loading...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  text: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
});
