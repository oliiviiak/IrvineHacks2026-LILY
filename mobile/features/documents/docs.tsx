import { useEffect, useState } from "react";
import { Dimensions, Pressable, ScrollView, StyleSheet, Text, View } from "react-native"
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

const SCREEN_WIDTH = Dimensions.get("window").width;
const SCREEN_HEIGHT = Dimensions.get("window").height;
const ITEM_GAP = 16;
const ITEM_WIDTH_CLOSED = 300;
const SNAP_INTERVAL_CLOSED = ITEM_WIDTH_CLOSED + ITEM_GAP;
const ITEM_WIDTH_OPEN = 200;
const SNAP_INTERVAL_OPEN = ITEM_WIDTH_OPEN + ITEM_GAP;

export function DocumentScreen(){
    const [barOpen, setBarOpen] = useState(false)
    const [snapBarOpen, setSnapBarOpen] = useState(false)
    const progress = useSharedValue(0) // 0 = closed, 1 = open
    const scrollRef = useAnimatedRef<Animated.ScrollView>()
    const currentIndex = useSharedValue(0)

    useEffect(() => {
        progress.value = withTiming(barOpen ? 1 : 0, { duration: 350, easing: Easing.inOut(Easing.cubic) })
        // Delay snapToInterval change until animation ends so the ScrollView
        // doesn't reset scroll position mid-animation
        const t = setTimeout(() => setSnapBarOpen(barOpen), 350)
        return () => clearTimeout(t)
    }, [barOpen])

    // Drive scroll position in sync with the animation so there's no jump
    useAnimatedReaction(
        () => progress.value,
        (p) => {
            const interval = interpolate(p, [0, 1], [SNAP_INTERVAL_CLOSED, SNAP_INTERVAL_OPEN])
            scrollTo(scrollRef, currentIndex.value * interval, 0, false)
        }
    )

    const snapInterval = snapBarOpen ? SNAP_INTERVAL_OPEN : SNAP_INTERVAL_CLOSED

    const containerAnimStyle = useAnimatedStyle(() => ({
        paddingTop: interpolate(progress.value, [0, 1], [SCREEN_WIDTH * 0.5, SCREEN_WIDTH * 0.33])
    }))

    const scrollContentAnimStyle = useAnimatedStyle(() => ({
        paddingHorizontal: interpolate(
            progress.value,
            [0, 1],
            [(SCREEN_WIDTH - ITEM_WIDTH_CLOSED) / 2, (SCREEN_WIDTH - ITEM_WIDTH_OPEN) / 2]
        )
    }))

    return (
        <View style={{ flex: 1 }}>
            <Animated.View style={[{ flex: 1 }, containerAnimStyle]}>
                <Animated.ScrollView
                    ref={scrollRef}
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    snapToInterval={snapInterval}
                    decelerationRate="fast"
                    onMomentumScrollEnd={(e) => {
                        currentIndex.value = Math.round(e.nativeEvent.contentOffset.x / snapInterval)
                    }}
                >
                    <Animated.View style={[{ flexDirection: "row" }, scrollContentAnimStyle]}>
                        <DocumentCard progress={progress} />
                        <DocumentCard progress={progress} />
                        <DocumentCard progress={progress} />
                        <DocumentCard progress={progress} />
                    </Animated.View>
                </Animated.ScrollView>
            </Animated.View>

            <DocumentBottomBar barOpen={barOpen} setBarOpen={setBarOpen} progress={progress} />
        </View>
    )
}

function DocumentCard({ progress }: { progress: SharedValue<number> }) {
    const animStyle = useAnimatedStyle(() => ({
        width: interpolate(progress.value, [0, 1], [ITEM_WIDTH_CLOSED, ITEM_WIDTH_OPEN])
    }))

    return (
        <Animated.View style={[styles.documentCard, animStyle]}>

        </Animated.View>
    )
}

function DocumentBottomBar({ barOpen: _barOpen, setBarOpen: _setBarOpen, progress }: { barOpen: boolean, setBarOpen: (v: boolean) => void, progress: SharedValue<number> }) {

    const insets = useSafeAreaInsets()

    const barAnimStyle = useAnimatedStyle(() => ({
        top: interpolate(progress.value, [0, 1], [SCREEN_HEIGHT * 0.75, SCREEN_HEIGHT * 0.50]),
        backgroundColor: interpolateColor(progress.value, [0, 1], ['transparent', '#F5F7F5']),
        borderColor: interpolateColor(progress.value, [0, 1], ['transparent', '#D3D3D3']),
    }))

    const chevronAnimStyle = useAnimatedStyle(() => ({
        opacity: progress.value,
    }))

    const swipeBarBorderAnimStyle = useAnimatedStyle(() => ({
        borderBottomWidth: interpolate(progress.value, [0, 1], [0, 1]),
        borderBottomColor: '#E5E3E3',
    }))

    return (
        <Animated.View style={[styles.documentBottomBar, barAnimStyle]}>
            <Animated.View style={swipeBarBorderAnimStyle}>
                <Pressable style={styles.swipeBar} onPress={() => _setBarOpen(!_barOpen)}>
                    <Animated.Text style={[styles.swipeBarChevron, chevronAnimStyle]}>∨</Animated.Text>
                </Pressable>
            </Animated.View>
            <ScrollView scrollEnabled={_barOpen} contentContainerStyle={{alignItems: "center", rowGap: 24, paddingBottom: insets.bottom, paddingTop: 24}}>
                <DocumentOverview />
                <AlertOverview />
            </ScrollView>
            {!_barOpen && (
                <Pressable style={StyleSheet.absoluteFillObject} onPress={() => _setBarOpen(true)} />
            )}
        </Animated.View>
    )
}

function DocumentOverview() {
    return (
        <View style={styles.documentOverview}>
            <Text style={[styles.cardHeader, {paddingBottom: 24}]}>In this document:</Text>
            <Text>
                AI RESPONSE GOES HERE BLAH BLAH BLAH BLAH BLAH BLAHBLAH BLAH BLAHBLAH BLAH
                AI RESPONSE GOES HERE BLAH BLAH BLAH BLAH BLAH BLAHBLAH BLAH BLAHBLAH BLAH
                AI RESPONSE GOES HERE BLAH BLAH BLAH BLAH BLAH BLAHBLAH BLAH BLAHBLAH BLAH
            </Text>
        </View>
    )
}

function AlertOverview() {
        return (
            <View style={styles.alertOverview}>
                <Text style={[styles.cardHeader, {paddingBottom: 24}]}>3 Alerts:</Text>
                <Text>
                    AI RESPONSE GOES HERE BLAH BLAH BLAH BLAH BLAH BLAHBLAH BLAH BLAHBLAH BLAH
                    AI RESPONSE GOES HERE BLAH BLAH BLAH BLAH BLAH BLAHBLAH BLAH BLAHBLAH BLAH
                    AI RESPONSE GOES HERE BLAH BLAH BLAH BLAH BLAH BLAHBLAH BLAH BLAHBLAH BLAH
                </Text>

            </View>
        )
}




const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: "#FFFFFF"
    },

    documentBottomBar: {
        position: "absolute",
        bottom: 0,
        width: "100%",
        borderTopLeftRadius: 37,
        borderTopRightRadius: 37,
        borderWidth: 1,
        overflow: "hidden",
    },

    documentOverview: {
        backgroundColor: "#A3DDA7",
        aspectRatio: 2,
        borderRadius: 11,
        width: "90%",
        paddingVertical: 28,
        paddingHorizontal: 20,
        shadowColor: "#000000",
        shadowOpacity: .1,
        shadowOffset: {width: 0, height: 0},
        shadowRadius: 6,
        paddingTop: 24,
    },

    alertOverview: {
        backgroundColor: "#FFFFFF",
        aspectRatio: 2,
        borderRadius: 11,
        width: "90%",
        borderColor: "#C9C9C9",
        borderWidth: 1,
        paddingVertical: 28,
        paddingHorizontal: 20,
        shadowColor: "#000000",
        shadowOpacity: .1,
        shadowOffset: {width: 0, height: 0},
        shadowRadius: 6
    },

    documentCard: {
        backgroundColor: "red",
        aspectRatio: .7,
        alignSelf: "flex-start",
        borderRadius: 10,
        borderColor: "#C1BFBF",
        borderWidth: 1,
        marginRight: ITEM_GAP,
    },

    swipeBar: {
        alignItems: "center",
        paddingTop: 14,
        paddingBottom: 8,
        borderBottomWidth: 1,
        borderColor: "#E5E3E3"
    },

    swipeBarChevron: {
        color: "#AAAAAA",
        fontSize: 18,
        lineHeight: 18,
    },

    cardHeader: {
        color: "#3B6157",
        fontFamily: "satoshi",
        fontWeight: "bold",
        fontSize: 16
    }
})
