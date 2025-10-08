import { Stack } from 'expo-router';
import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { SafeAreaProvider } from 'react-native-safe-area-context';

export default function RootLayout() {
  const loadToken = useAuthStore((state) => state.loadToken);

  useEffect(() => {
    loadToken();
  }, []);

  return (
    <SafeAreaProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(customer)" />
        <Stack.Screen name="(delivery)" />
        <Stack.Screen name="(admin)" />
        <Stack.Screen name="login" />
        <Stack.Screen name="register" />
      </Stack>
    </SafeAreaProvider>
  );
}
