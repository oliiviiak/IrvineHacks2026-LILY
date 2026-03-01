import React from "react";
import { DocumentScreen  }from "@/features/documents/docs"
import { ConvoContextProvider } from "@/features/convo/convo-context";

export default function DocumentPage(){
    return (
        <ConvoContextProvider>
            <DocumentScreen />
        </ConvoContextProvider>
    )
}