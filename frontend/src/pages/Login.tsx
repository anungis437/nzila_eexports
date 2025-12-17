import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useLanguage } from '../contexts/LanguageContext'
import { Button } from '../components/ui/button'
import { Car, LogIn, Globe } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Login() {
  const { login } = useAuth()
  const { language, changeLanguage } = useLanguage()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const emailInputRef = useRef<HTMLInputElement>(null)

  // Auto-focus email input on mount for accessibility
  useEffect(() => {
    emailInputRef.current?.focus()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      {/* Skip to main content link for keyboard users */}
      <a
        href="#login-form"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-primary-600 focus:rounded-lg focus:shadow-lg"
      >
        {language === 'fr' ? 'Aller au formulaire de connexion' : 'Skip to login form'}
      </a>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
        role="main"
        aria-label={language === 'fr' ? 'Page de connexion' : 'Login page'}
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div 
            className="inline-flex items-center justify-center w-16 h-16 gradient-primary rounded-2xl shadow-xl shadow-primary-500/30 mb-4"
            role="img"
            aria-label="Nzila Export Hub Logo"
          >
            <Car className="w-8 h-8 text-white" aria-hidden="true" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Nzila Export Hub
          </h1>
          <p className="text-slate-500">
            {language === 'fr' ? 'Connectez-vous à votre compte' : 'Sign in to your account'}
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-100">
          <form 
            id="login-form"
            onSubmit={handleSubmit} 
            className="space-y-6"
            aria-label={language === 'fr' ? 'Formulaire de connexion' : 'Login form'}
            noValidate
          >
            <div>
              <label 
                htmlFor="email-input"
                className="block text-sm font-medium text-slate-700 mb-2"
              >
                {language === 'fr' ? 'Email' : 'Email'}
                <span className="text-red-500 ml-1" aria-label="required">*</span>
              </label>
              <input
                id="email-input"
                ref={emailInputRef}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                placeholder={language === 'fr' ? 'votre@email.com' : 'your@email.com'}
                autoComplete="email"
                required
                aria-required="true"
                aria-invalid={!!error}
                aria-describedby={error ? 'login-error' : undefined}
              />
            </div>

            <div>
              <label 
                htmlFor="password-input"
                className="block text-sm font-medium text-slate-700 mb-2"
              >
                {language === 'fr' ? 'Mot de passe' : 'Password'}
                <span className="text-red-500 ml-1" aria-label="required">*</span>
              </label>
              <input
                id="password-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                placeholder="••••••••"
                autoComplete="current-password"
                required
                aria-required="true"
                aria-invalid={!!error}
                aria-describedby={error ? 'login-error' : undefined}
              />
            </div>

            {error && (
              <div 
                id="login-error"
                role="alert"
                aria-live="assertive"
                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
              >
                <span className="sr-only">{language === 'fr' ? 'Erreur:' : 'Error:'}</span>
                {error}
              </div>
            )}

            <Button 
              type="submit" 
              className="w-full" 
              size="lg" 
              disabled={loading}
              aria-label={loading ? (language === 'fr' ? 'Connexion en cours...' : 'Signing in...') : (language === 'fr' ? 'Se connecter' : 'Sign in')}
            >
              <LogIn className="w-5 h-5 mr-2" aria-hidden="true" />
              {loading ? (language === 'fr' ? 'Connexion...' : 'Signing in...') : (language === 'fr' ? 'Se connecter' : 'Sign In')}
            </Button>
          </form>

          {/* Language Toggle */}
          <div className="mt-6 pt-6 border-t border-slate-100">
            <button
              onClick={() => changeLanguage(language === 'en' ? 'fr' : 'en')}
              className="w-full flex items-center justify-center gap-2 text-slate-600 hover:text-slate-900 transition"
              aria-label={language === 'en' ? 'Changer la langue en français' : 'Change language to English'}
            >
              <Globe className="w-4 h-4" aria-hidden="true" />
              <span className="text-sm">{language === 'en' ? 'Français' : 'English'}</span>
            </button>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="mt-4 text-center" role="complementary" aria-label="Demo credentials">
          <p className="text-xs text-slate-500">
            {language === 'fr' ? 'Démo:' : 'Demo:'} admin / password
          </p>
        </div>
      </motion.div>
    </div>
  )
}
