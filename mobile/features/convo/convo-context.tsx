// mobile/features/convo/convo-context.tsx

import { BASE_URL } from '@/constants/urls';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '../auth/user-context';

const NEEDER_ID = '00000000-0000-0000-0000-000000000001';
const POLL_MS = 5000;

type ConvoContextType = {
    convoId: string | null;
    isLoading: boolean;
};

const ConvoContext = createContext<ConvoContextType | undefined>(undefined);

export function ConvoContextProvider({ children }: { children: React.ReactNode }) {
    const [convoId, setConvoId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const { fetchWithAuth, isLoggedIn } = useUser();

    const fetchLatestConvo = async () => {
        try {
            const res = await fetchWithAuth(`${BASE_URL}/convo/latest/${NEEDER_ID}`);
            if (res.ok) {
                const data = await res.json() as {convo_id: string};
                setConvoId(data.convo_id);
            }
        } catch (e) {
            console.error('Error fetching latest convo:', e);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (!isLoggedIn) return;

        fetchLatestConvo();

        // Keep polling so the app picks up new convos as the microcontroller creates them
        const interval = setInterval(fetchLatestConvo, POLL_MS);
        return () => clearInterval(interval);
    }, [isLoggedIn]);

    return (
        <ConvoContext.Provider value={{ convoId, isLoading }}>
            {children}
        </ConvoContext.Provider>
    );
}

export const useConvo = () => {
    const ctx = useContext(ConvoContext);
    if (!ctx) throw new Error('useConvo must be inside ConvoContextProvider');
    return ctx;
};