import { Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native"
import { DocumentCollection } from "./doc"
import { GREY_1, TEXT_GREY } from "@/constants/colors"

export function DocumentView(){
    return (
        <View style={{paddingBottom: 32}}>
            <Text style={{fontFamily: "satoshi", fontWeight: "700", fontSize: 26, paddingHorizontal: 25, paddingBottom: 12}}>Folders </Text>
            <ScrollView showsHorizontalScrollIndicator={false} contentContainerStyle={{paddingHorizontal: 25, flexDirection: "row", columnGap: 12}} horizontal={true}>
                <Folder></Folder>
                <Folder></Folder>
                <Folder></Folder>
                <Folder></Folder>
            </ScrollView>
        </View>
    )
}


const FolderImage = require("@/features/documents/folder.png") 
export function Folder(){
    return (
        <Pressable style={style.folderContainer}>
            <Image source={FolderImage}></Image>
            <Text style={{fontFamily: "satoshi", fontSize: 14, fontWeight: "bold"}}>Medical documents</Text>
        </Pressable>
    )
}

export function RecentDocument({ dc } : {dc? : DocumentCollection}){
    return (
        <View style={style.container}>
            <Image source={{uri: "https://fastly.picsum.photos/id/237/200/300.jpg?hmac=TmmQSbShHz9CdQm0NkEjx1Dyh_Y984R9LpNrpvH2D_U"}} style={style.docPreview}></Image>
            <View style={style.docContentContainer}>
                <View style={style.docContent}>
                    <Text style={style.docTitle}>Document Title</Text>
                    <Text style={style.docInfo}>1/23/26  •  3 pages</Text>
                </View>

                <View style={style.docBottomRow}>
                    <Text>Type: medical</Text>
                    <Text>Review</Text>
                </View>


            </View>
        </View>
    ) 
}

const style = StyleSheet.create({
    container: {
        backgroundColor: GREY_1,
        flexDirection: "row",
        columnGap: 12,
        height: 150,
        paddingVertical: 16,
        paddingLeft: 16,
        paddingRight: 20,
        borderRadius: 11,
        borderColor: "#E0E9E0",
        borderWidth: 1,
    },

    docPreview: {
        height: "100%",
        aspectRatio: .66,
        resizeMode: "cover",
        borderRadius: 9,
        borderColor: "#D7D7D7",
        borderWidth: 1,
    },

    docContentContainer: {
        flex: 1,
        flexDirection: "column",
        justifyContent: "space-between",
        paddingVertical: 8,
        paddingRight: 8,
    },

    docContent: {
        
    },

    docTitle: {
        fontFamily: "satoshi",
        fontWeight: 700,
        fontSize: 18
    },

    docInfo: {
        fontFamily: "inter",
        fontStyle: "normal",
        color: TEXT_GREY
    },

    docBottomRow: {
        flexDirection: "row",
        justifyContent: "space-between"
    },

    docButton: {

    },

    folderContainer: {
        rowGap: 6,
        alignItems: "center",
    }

    





})