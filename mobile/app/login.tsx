import { useUser } from "@/features/auth/user-context";
import { Button } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Login(){

    const user = useUser()

    return(
        <SafeAreaView>
            <Button title={"press me"} onPress={()=> { user.signIn("") }}>

            </Button>
        </SafeAreaView>
    )
}