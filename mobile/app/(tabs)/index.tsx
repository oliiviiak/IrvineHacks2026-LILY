import { DocumentView, Folder, RecentDocument } from "@/features/documents/doc-view";
import { AlertNotice } from "@/features/home/home-view";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

export default function Home(){
    const insets = useSafeAreaInsets()
    return (
        <ScrollView contentContainerStyle={{paddingTop: insets.top, paddingBottom: insets.bottom, paddingHorizontal: 25 }}>
            <Text style={style.recentsTitle}>Alerts</Text>
            <AlertNotice></AlertNotice>
        </ScrollView>
    )
}

const style = StyleSheet.create({
    recentsTitle: {
        fontFamily: "satoshi",
        fontWeight: "700",
        fontSize: 26,
    }
})