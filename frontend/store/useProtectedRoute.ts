import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { useAuthStore } from './authStore';

export const useProtectedRoute = () => {
  const { isAuthenticated, isLoading, user } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && user) {
        switch (user.role) {
          case 'customer':
            router.replace('/(customer)/home');
            break;
          case 'delivery_agent':
            router.replace('/(delivery)/orders');
            break;
          case 'admin':
            router.replace('/(admin)/dashboard');
            break;
          default:
            router.replace('/login');
        }
      } else {
        router.replace('/login');
      }
    }
  }, [isAuthenticated, isLoading, user, router]);
};
