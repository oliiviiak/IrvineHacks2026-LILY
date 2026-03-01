import { UserContextProvider, useUser } from '@/features/auth/user-context';
import { router, Stack } from 'expo-router';
import { useEffect } from 'react';

export default function Layout() {
  return (
    <UserContextProvider>
      <AppNavigator />
    </UserContextProvider>
  );
}

function AppNavigator(){

  const user = useUser()

  useEffect(() => {
    if (user.isLoading) return;

    router.replace({
        pathname: user.isLoggedIn ? "/document" : '/login',
        params: {}
    })

  }, [user.isLoggedIn, user.isLoading])


  return(
    <Stack>
        <Stack.Protected guard={user.isLoggedIn}>
            <Stack.Screen name="(tabs)" options={{ headerShown: false }}/>
            <Stack.Screen name="document" options={{ headerShown: false }}/>
        </Stack.Protected>        
        <Stack.Screen name="login" options={{ headerShown: false }} />
    </Stack>
  )
} 