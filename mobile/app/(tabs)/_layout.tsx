import { Stack, Tabs } from 'expo-router';

export default function Layout() {
  return (
  <Tabs screenOptions={{ tabBarActiveTintColor: 'blue', headerShown: false }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
        }}
      />
      <Tabs.Screen
        name="docs"
        options={{
          title: 'Docs',
        }}
      />
    </Tabs>
  );
}
