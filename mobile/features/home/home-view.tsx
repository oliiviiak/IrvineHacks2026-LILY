import { Image, Pressable, StyleSheet, Text, View } from "react-native";


export function HomeReviewHeader() {

} 

export function AlertNotice() {
    return(

        <Pressable style={style.alertNoticeContainer}>
            <Image source={{uri: "https://fastly.picsum.photos/id/237/200/300.jpg?hmac=TmmQSbShHz9CdQm0NkEjx1Dyh_Y984R9LpNrpvH2D_U"}} style={style.docPreview}></Image>
            <View style={style.alertNoticeContent}>
                <View style={{flexDirection: "row", justifyContent: "space-between"}}>
                    <Text style={style.alertNoticeName}>Document Title</Text> 
                    <Text style={style.alertNoticeDate}>1/23/26</Text> 
                </View>
                <Text style={style.alertNoticeNumber}>4 Alerts</Text> 
            </View>
        </Pressable>
    )
}


const style = StyleSheet.create({
    reviewHeader: {
        experimental_backgroundImage: "linear-gradient(to right,)"
    },

    alertNoticeName: {
        fontFamily: "satoshi",
        fontWeight: "bold",
        fontSize: 16
    },

    alertNoticeNumber: {
        color: "#858585",
        fontFamily: "inter",
        fontSize: 14
    },
    
    alertNoticeDate: {
        color: "#858585",
        fontFamily: "inter",
        fontSize: 14
    },



    alertNoticeContent: {
        rowGap: 4,
        height: "100%",
        flex: 1,
    },

    alertNoticeContainer: {
        padding: 16,
        flexDirection: "row",
        columnGap: 16,
        backgroundColor: "#F5F7F5",
        borderColor: "#D8E4D8",
        borderWidth: 1,
        borderRadius: 11,
        width: "100%",
        height: 100,
        flex: 1,
    },

    docPreview: {
        flex: 0,
        height: "100%",
        aspectRatio: .66,
        resizeMode: "cover",
        borderRadius: 9,
        borderColor: "#D7D7D7",
        borderWidth: 1,
    },
})

