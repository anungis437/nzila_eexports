import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
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
  is_staff?: boolean
  is_superuser?: boolean
  is_active?: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (data: any) => Promise<void>
  isAuthenticated: boolean
  isAdmin: boolean
  isSuperuser: boolean
  isStaff: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    try {
      // Try to load user from API (token is in httpOnly cookie)
      const userData = await apiClient.getCurrentUser()
      setUser(userData)
    } catch (error) {
      // User not authenticated or token expired - this is normal if not logged in
      console.error('Failed to load user:', error)
      localStorage.removeItem('user')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

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
        isAdmin: user?.role === 'admin' || user?.is_staff || user?.is_superuser || false,
        isSuperuser: user?.is_superuser || false,
        isStaff: user?.is_staff || false,
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
