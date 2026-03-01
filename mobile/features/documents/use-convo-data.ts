// mobile/features/documents/use-convo-data.ts

import { BASE_URL } from '@/constants/urls';
import { useEffect, useState } from 'react';
import { useUser } from '../auth/user-context';

export type DocumentData = {
    document_id: string;
    convo_id: string;
    created_at: string;
    url: string | null;
    overview: string;
    content: string;
};

export type AlertData = {
    alert_id: string;
    doc_id: string;
    timestamp: string;
    message: string;
};

type ConvoData = {
    transcripts: any[];
    alerts: AlertData[];
    documents: DocumentData[];
};

export function useConvoData(convoId: string | null) {
    const { fetchWithAuth } = useUser();
    const [documents, setDocuments] = useState<DocumentData[]>([]);
    const [alerts, setAlerts] = useState<AlertData[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const refresh = async () => {
        if (!convoId) return;
        setIsLoading(true);
        setError(null);
        try {
            const res = await fetchWithAuth(`${BASE_URL}/convo/${convoId}`);
            if (!res.ok) throw new Error('Failed to fetch convo data');
            const data: ConvoData = await res.json() as ConvoData;
            setDocuments(data.documents ?? []);
            setAlerts(data.alerts ?? []);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        refresh();
    }, [convoId]);

    return { documents, alerts, isLoading, error, refresh };
}