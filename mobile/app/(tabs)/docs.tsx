import { DocumentView, Folder, RecentDocument } from "@/features/documents/doc-view";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

export default function Docs(){
    const insets = useSafeAreaInsets()
    return (
        <ScrollView contentContainerStyle={{paddingTop: insets.top, paddingBottom: insets.bottom, }}>
            <DocumentView></DocumentView>
            <View style={{rowGap: 10, paddingHorizontal: 25}}>
                <Text style={style.recentsTitle}>Recents</Text>
                <RecentDocument/>
                <RecentDocument/>
                <RecentDocument/>       
            </View>
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