import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { apiClient } from '../lib/api'

interface User {
  id: number
  email: string
  username: string
  first_name: string
  last_name: string
  full_name: string
  role: 'admin' | 'dealer' | 'broker' | 'buyer'
  company_name?: string
  phone?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (data: any) => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      // Try to load user from API (token is in httpOnly cookie)
      const userData = await apiClient.getCurrentUser()
      setUser(userData)
    } catch (error) {
      // User not authenticated or token expired
      console.error('Failed to load user:', error)
      localStorage.removeItem('user')
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    await apiClient.login(email, password)
    await loadUser()
  }

  const logout = () => {
    apiClient.logout()
    setUser(null)
  }

  const register = async (data: any) => {
    await apiClient.register(data)
    if (data.email && data.password) {
      await login(data.email, data.password)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        register,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
