// mobile/features/documents/docs.tsx  (REPLACE existing)

import { BASE_URL } from '@/constants/urls';
import { useConvo } from '@/features/convo/convo-context';
import { useEffect, useRef, useState } from "react";
import {
    ActivityIndicator,
    Dimensions,
    Image,
    Pressable,
    ScrollView,
    StyleSheet,
    Text,
    View,
} from "react-native";
import Animated, {
    Easing,
    interpolate,
    interpolateColor,
    scrollTo,
    SharedValue,
    useAnimatedReaction,
    useAnimatedRef,
    useAnimatedStyle,
    useSharedValue,
    withTiming,
} from "react-native-reanimated";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { AlertData, DocumentData, useConvoData } from './use-convo-data';
import Markdown from 'react-native-markdown-display';

const SCREEN_WIDTH         = Dimensions.get("window").width;
const SCREEN_HEIGHT        = Dimensions.get("window").height;
const ITEM_GAP             = 16;
const ITEM_WIDTH_CLOSED    = 300;
const SNAP_INTERVAL_CLOSED = ITEM_WIDTH_CLOSED + ITEM_GAP;
const ITEM_WIDTH_OPEN      = 200;
const SNAP_INTERVAL_OPEN   = ITEM_WIDTH_OPEN + ITEM_GAP;
const POLL_MS              = 5000;

// ─────────────────────────────────────────────────────────────────────────────

export function DocumentScreen() {
    const [barOpen, setBarOpen]         = useState(false);
    const [snapBarOpen, setSnapBarOpen] = useState(false);
    const [pageIndex, setPageIndex]     = useState(0);

    const progress   = useSharedValue(0);
    const scrollRef  = useAnimatedRef<Animated.ScrollView>();
    const currentIdx = useSharedValue(0);
    const pollRef    = useRef<ReturnType<typeof setInterval> | null>(null);

    const { convoId }                               = useConvo();
    const { documents, alerts, isLoading, refresh } = useConvoData(convoId);

    const selectedDoc: DocumentData | null    = documents[pageIndex] ?? null;
    const selectedAlerts: AlertData[]         = selectedDoc
        ? alerts.filter(a => a.doc_id === selectedDoc.document_id)
        : [];

    // Poll for new docs while screen is mounted
    useEffect(() => {
        if (!convoId) return;
        pollRef.current = setInterval(refresh, POLL_MS);
        return () => { if (pollRef.current) clearInterval(pollRef.current); };
    }, [convoId]);

    // Animate open/close
    useEffect(() => {
        progress.value = withTiming(barOpen ? 1 : 0, {
            duration: 350,
            easing: Easing.inOut(Easing.cubic),
        });
        const t = setTimeout(() => setSnapBarOpen(barOpen), 350);
        return () => clearTimeout(t);
    }, [barOpen]);

    // Keep scroll in sync with animation
    useAnimatedReaction(
        () => progress.value,
        (p) => {
            const interval = interpolate(p, [0, 1], [SNAP_INTERVAL_CLOSED, SNAP_INTERVAL_OPEN]);
            scrollTo(scrollRef, currentIdx.value * interval, 0, false);
        }
    );

    const snapInterval = snapBarOpen ? SNAP_INTERVAL_OPEN : SNAP_INTERVAL_CLOSED;

    const containerAnimStyle = useAnimatedStyle(() => ({
        paddingTop: interpolate(
            progress.value,
            [0, 1],
            [SCREEN_WIDTH * 0.5, SCREEN_WIDTH * 0.33]
        ),
    }));

    const scrollContentAnimStyle = useAnimatedStyle(() => ({
        paddingHorizontal: interpolate(
            progress.value,
            [0, 1],
            [(SCREEN_WIDTH - ITEM_WIDTH_CLOSED) / 2, (SCREEN_WIDTH - ITEM_WIDTH_OPEN) / 2]
        ),
    }));

    if (isLoading && documents.length === 0) {
        return (
            <View style={styles.centered}>
                <ActivityIndicator size="large" color="#4BB854" />
            </View>
        );
    }

    if (documents.length === 0) {
        return (
            <View style={styles.centered}>
                <Text style={styles.emptyText}>
                    No documents yet.{"\n"}Say "Hey Lily" and hold up a document.
                </Text>
            </View>
        );
    }

    return (
        <View style={{ flex: 1 }}>
            {/* Page counter: "1 of 3" */}
            <PageCounter current={pageIndex + 1} total={documents.length} />

            <Animated.View style={[{ flex: 1 }, containerAnimStyle]}>
                <Animated.ScrollView
                    ref={scrollRef}
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    snapToInterval={snapInterval}
                    decelerationRate="fast"
                    onMomentumScrollEnd={(e) => {
                        const idx = Math.round(
                            e.nativeEvent.contentOffset.x / snapInterval
                        );
                        currentIdx.value = idx;
                        setPageIndex(idx);
                    }}
                >
                    <Animated.View style={[{ flexDirection: "row" }, scrollContentAnimStyle]}>
                        {documents.map((doc, i) => (
                            <DocumentCard
                                key={doc.document_id}
                                doc={doc}
                                progress={progress}
                            />
                        ))}
                    </Animated.View>
                </Animated.ScrollView>
            </Animated.View>

            <DocumentBottomBar
                barOpen={barOpen}
                setBarOpen={setBarOpen}
                progress={progress}
                document={selectedDoc}
                alerts={selectedAlerts}
            />
        </View>
    );
}

// ─── Page counter ─────────────────────────────────────────────────────────────

function PageCounter({ current, total }: { current: number; total: number }) {
    return (
        <View style={styles.pageCounter}>
            <Text style={styles.pageCounterText}>
                {current} of {total}
            </Text>
        </View>
    );
}

// ─── Document card ────────────────────────────────────────────────────────────

function DocumentCard({
    doc,
    progress,
}: {
    doc: DocumentData;
    progress: SharedValue<number>;
}) {
    const animStyle = useAnimatedStyle(() => ({
        width: interpolate(progress.value, [0, 1], [ITEM_WIDTH_CLOSED, ITEM_WIDTH_OPEN]),
    }));

    return (
        <Animated.View style={[styles.documentCard, animStyle]}>
            {doc.url ? (
                <Image
                    source={{ uri: doc.url }}
                    style={StyleSheet.absoluteFillObject}
                    resizeMode="cover"
                />
            ) : (
                <View style={[StyleSheet.absoluteFillObject, styles.docPlaceholder]}>
                    <Text style={styles.docPlaceholderText}>📄</Text>
                </View>
            )}
        </Animated.View>
    );
}

// ─── Bottom bar ───────────────────────────────────────────────────────────────

function DocumentBottomBar({
    barOpen,
    setBarOpen,
    progress,
    document,
    alerts,
}: {
    barOpen: boolean;
    setBarOpen: (v: boolean) => void;
    progress: SharedValue<number>;
    document: DocumentData | null;
    alerts: AlertData[];
}) {
    const insets = useSafeAreaInsets();

    const barAnimStyle = useAnimatedStyle(() => ({
        top: interpolate(
            progress.value,
            [0, 1],
            [SCREEN_HEIGHT * 0.75, SCREEN_HEIGHT * 0.5]
        ),
        backgroundColor: interpolateColor(
            progress.value,
            [0, 1],
            ["transparent", "#F5F7F5"]
        ),
        borderColor: interpolateColor(
            progress.value,
            [0, 1],
            ["transparent", "#D3D3D3"]
        ),
    }));

    const chevronAnimStyle = useAnimatedStyle(() => ({
        opacity: progress.value,
        transform: [
            { rotate: `${interpolate(progress.value, [0, 1], [0, 180])}deg` },
        ],
    }));

    const swipeBarBorderAnimStyle = useAnimatedStyle(() => ({
        borderBottomWidth: interpolate(progress.value, [0, 1], [0, 1]),
        borderBottomColor: "#E5E3E3",
    }));

    return (
        <Animated.View style={[styles.bottomBar, barAnimStyle]}>
            {/* Drag handle / chevron */}
            <Animated.View style={swipeBarBorderAnimStyle}>
                <Pressable
                    style={styles.swipeBar}
                    onPress={() => setBarOpen(!barOpen)}
                >
                    <Animated.Text style={[styles.chevron, chevronAnimStyle]}>
                        ∨
                    </Animated.Text>
                </Pressable>
            </Animated.View>

            <ScrollView
                scrollEnabled={barOpen}
                contentContainerStyle={{
                    alignItems: "center",
                    rowGap: 16,
                    paddingBottom: insets.bottom + 24,
                    paddingTop: 24,
                }}
            >
                <DocumentOverview document={document} />
                <AlertsCard alerts={alerts} />
            </ScrollView>

            {/* Tap anywhere to open when collapsed */}
            {!barOpen && (
                <Pressable
                    style={StyleSheet.absoluteFillObject}
                    onPress={() => setBarOpen(true)}
                />
            )}
        </Animated.View>
    );
}

// ─── Overview card ────────────────────────────────────────────────────────────

function DocumentOverview({ document }: { document: DocumentData | null }) {
    return (
        <View style={styles.overviewCard}>
            <Text style={styles.alertTitle}>In this document:</Text>
            {document?.overview ? (
                <Markdown style={{
                    body: { fontFamily: 'inter', fontSize: 14, lineHeight: 20, color: '#2D4F3E' },
                    strong: { fontFamily: 'satoshi', fontWeight: '700' as const, color: '#1A3B2F' },
                    heading1: { fontFamily: 'satoshi', fontWeight: '700' as const, fontSize: 16, color: '#1A3B2F' },
                    heading2: { fontFamily: 'satoshi', fontWeight: '700' as const, fontSize: 15, color: '#1A3B2F' },
                    bullet_list_icon: { color: '#2D4F3E' },
                }}>
                    {document.overview}
                </Markdown>
            ) : (
                <Text style={styles.overviewBody}>
                    Select a document to see the summary.
                </Text>
            )}
        </View>
    );
}

// ─── Alerts card ──────────────────────────────────────────────────────────────

function AlertsCard({ alerts }: { alerts: AlertData[] }) {
    return (
        <View style={styles.alertsCard}>
            <Text style={styles.alertsCount}>
                {alerts.length > 0
                    ? `${alerts.length} Alert${alerts.length > 1 ? "s" : ""}`
                    : "No alerts"}
            </Text>

            {alerts.map((alert, i) => (
                <View key={alert.alert_id ?? i} style={styles.alertRow}>
                    <Text style={styles.alertTitle}>
                        Page {i + 1}: {alertTitle(alert.message)}
                    </Text>
                    <Text style={styles.alertBody}>{alertBody(alert.message)}</Text>
                </View>
            ))}

            {alerts.length === 0 && (
                <Text style={styles.overviewBody}>
                    No action required for this document.
                </Text>
            )}
        </View>
    );
}

// Split alert message into a short title + rest of text
function alertTitle(message: string): string {
    return message.split(".")[0] ?? message;
}
function alertBody(message: string): string {
    const rest = message.split(".").slice(1).join(".").trim();
    return rest || message;
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
    centered: {
        flex: 1,
        alignItems: "center",
        justifyContent: "center",
        paddingHorizontal: 40,
    },
    emptyText: {
        textAlign: "center",
        color: "#858585",
        fontFamily: "inter",
        fontSize: 16,
        lineHeight: 24,
    },

    // Page counter
    pageCounter: {
        position: "absolute",
        top: 60,
        alignSelf: "center",
        zIndex: 10,
        flexDirection: "row",
        alignItems: "center",
        backgroundColor: "rgba(255,255,255,0.85)",
        paddingHorizontal: 14,
        paddingVertical: 6,
        borderRadius: 20,
        shadowColor: "#000",
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 1 },
        shadowRadius: 4,
    },
    pageCounterText: {
        fontFamily: "inter",
        fontSize: 13,
        color: "#555",
    },

    // Card
    documentCard: {
        aspectRatio: 0.7,
        alignSelf: "flex-start",
        borderRadius: 10,
        borderColor: "#C1BFBF",
        borderWidth: 1,
        marginRight: ITEM_GAP,
        overflow: "hidden",
        backgroundColor: "#E8F4E8",
    },
    docPlaceholder: {
        alignItems: "center",
        justifyContent: "center",
    },
    docPlaceholderText: {
        fontSize: 48,
    },

    // Bottom bar
    bottomBar: {
        position: "absolute",
        bottom: 0,
        width: "100%",
        borderTopLeftRadius: 37,
        borderTopRightRadius: 37,
        borderWidth: 1,
        overflow: "hidden",
    },
    swipeBar: {
        alignItems: "center",
        paddingTop: 14,
        paddingBottom: 10,
    },
    chevron: {
        color: "#AAAAAA",
        fontSize: 18,
        lineHeight: 18,
    },

    // Overview card
    overviewCard: {
        backgroundColor: "#A3DDA7",
        width: "90%",
        borderRadius: 11,
        paddingVertical: 24,
        paddingHorizontal: 20,
        gap: 6,
        shadowColor: "#000",
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 0 },
        shadowRadius: 6,
    },
    cardLabel: {
        fontFamily: "inter",
        fontSize: 13,
        color: "#3B6157",
        marginBottom: 4,
    },
    overviewHeading: {
        fontFamily: "satoshi",
        fontWeight: "700",
        fontSize: 18,
        color: "#1A3B2F",
        marginBottom: 6,
    },
    overviewBullet: {
        fontFamily: "inter",
        fontSize: 14,
        lineHeight: 20,
        color: "#2D4F3E",
    },
    overviewBody: {
        fontFamily: "inter",
        fontSize: 14,
        color: "#555",
        lineHeight: 20,
    },

    // Alerts card
    alertsCard: {
        backgroundColor: "#FFFFFF",
        width: "90%",
        borderRadius: 11,
        borderColor: "#C9C9C9",
        borderWidth: 1,
        paddingVertical: 24,
        paddingHorizontal: 20,
        gap: 12,
        shadowColor: "#000",
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 0 },
        shadowRadius: 6,
    },
    alertsCount: {
        fontFamily: "satoshi",
        fontWeight: "700",
        fontSize: 16,
        color: "#333",
        marginBottom: 4,
    },
    alertRow: {
        gap: 2,
    },
    alertTitle: {
        fontFamily: "satoshi",
        fontWeight: "700",
        fontSize: 15,
        color: "#1A1A1A",
    },
    alertBody: {
        fontFamily: "inter",
        fontSize: 13,
        color: "#555",
        lineHeight: 18,
    },
});