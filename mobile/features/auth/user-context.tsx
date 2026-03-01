import { BASE_URL } from '@/constants/urls'
import * as SecureStore from 'expo-secure-store'
import React, { useContext, useEffect, useState } from "react"
import { View } from 'react-native'



type UserContextType = {
    isLoading: boolean,
    isLoggedIn: boolean

    signIn: (email: string) => Promise<void>,
    signOut: () => Promise<void>

    fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>,
    error: Error | null,
}

const UserContext = React.createContext<UserContextType | undefined>(undefined)

export function UserContextProvider({children} : {children: React.ReactNode}){
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = React.useState<Error | null>(null)


    useEffect(() => {
        restoreSession()
    }, [])


    const setAccessToken = async (access_token: string) => {
        await SecureStore.setItemAsync("access_token", access_token)
    }

    const getAccessToken = async () => {
        return SecureStore.getItemAsync("access_token")
    }

    const removeAccessToken = async () => {
        try {
            await SecureStore.deleteItemAsync("access_token")
            return true
        } 
        catch(error) {
            return false
        }
    }
    
    const AUTH_URL = `${BASE_URL}/auth/session`
    const restoreSession = async () => {
        setIsLoading(true)
        try {

            const access_token = await getAccessToken()
            const res = await fetchWithAuth(AUTH_URL)
            if (res.ok) setIsLoggedIn(true)
            else await removeAccessToken()
        }
        catch (error) {
            console.error(`error restoring session: ${error}`)
            await removeAccessToken()
        } 

        finally {
            setIsLoading(false)
        }

    }


    const signIn = async (email: string) => {
        const test_login = {
            "provider": "email",
            "oauth_code": "",
            "email": "test@gmail.com"
        }
        console.log(AUTH_URL)

        try {

            const authRes = await fetch(AUTH_URL, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(test_login)
            });

            if (!authRes.ok) {
                throw new Error("Sign in failed.")
            }

            let tokens = await authRes.json() as {
                "session_token": string
            }

            const new_access_token = tokens["session_token"]
            if(new_access_token){
                await setAccessToken(new_access_token)
                setIsLoggedIn(true)
            } 
            
        }

        catch (error) {
            console.log(`error signing in: ${error}`)
        }

    }

    const signOut = async () => {
        try {
            await fetchWithAuth(AUTH_URL, {
                method: "DELETE"
            });
        }

        catch (error) {
            console.error(`error during logout: ${error}`)
        }

        await removeAccessToken()
        setIsLoggedIn(false)
    }

    const fetchWithAuth = async (url: string, options?: RequestInit) => {

        let access_token = await getAccessToken()

        const response = await fetch(url, {
            ...options,
            headers: {
                ...options?.headers,
                Authorization: `Bearer ${access_token}`
            }
        })

        if (response.status === 401){
            setIsLoggedIn(false)
        }

        return response
    }

    const value: UserContextType = {
        isLoggedIn: isLoggedIn,
        isLoading: isLoading,
        signIn: signIn,
        signOut: signOut,

        fetchWithAuth: fetchWithAuth,
        error: error
    }    

    return (
        <UserContext.Provider value={value}>
            {children}
        </UserContext.Provider>
    )    
}

export const useUser = () => {
    const context = useContext(UserContext)
    if (!context) {
        throw new Error("useUser must be within a user provider");
    }

    return context
}