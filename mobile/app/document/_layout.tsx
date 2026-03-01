import { UserContextProvider, useUser } from '@/features/auth/user-context';
import { router, Stack } from 'expo-router';
import { useEffect } from 'react';

export default function Layout() {
  
  return(
    <Stack>
        <Stack.Screen name="index" options={{ headerShown: false }}/>
    </Stack>
  )
} 