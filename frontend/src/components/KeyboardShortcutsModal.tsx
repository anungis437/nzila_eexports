import { useEffect } from 'react'
import { X, Command } from 'lucide-react'

interface KeyboardShortcutsModalProps {
  isOpen: boolean
  onClose: () => void
  language?: 'en' | 'fr'
}

export default function KeyboardShortcutsModal({ isOpen, onClose, language = 'en' }: KeyboardShortcutsModalProps) {
  // Handle Escape key to close
  useEffect(() => {
    if (!isOpen) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  // Focus trap: keep focus within modal
  useEffect(() => {
    if (!isOpen) return

    const modal = document.getElementById('keyboard-shortcuts-modal')
    if (!modal) return

    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement?.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement?.focus()
        }
      }
    }

    modal.addEventListener('keydown', handleTab as any)
    firstElement?.focus()

    return () => {
      modal.removeEventListener('keydown', handleTab as any)
    }
  }, [isOpen])

  if (!isOpen) return null

  const t = (en: string, fr: string) => (language === 'fr' ? fr : en)

  const shortcuts = [
    {
      category: t('Navigation', 'Navigation'),
      items: [
        { keys: ['Tab'], description: t('Move to next element', 'Aller à l\'élément suivant') },
        { keys: ['Shift', 'Tab'], description: t('Move to previous element', 'Aller à l\'élément précédent') },
        { keys: ['Enter'], description: t('Activate button or link', 'Activer un bouton ou un lien') },
        { keys: ['Esc'], description: t('Close modal or cancel', 'Fermer le modal ou annuler') },
        { keys: ['Cmd/Ctrl', 'K'], description: t('Open global search', 'Ouvrir la recherche globale') },
      ],
    },
    {
      category: t('Tabs', 'Onglets'),
      items: [
        { keys: ['←', '→'], description: t('Navigate between tabs', 'Naviguer entre les onglets') },
        { keys: ['Home'], description: t('Go to first tab', 'Aller au premier onglet') },
        { keys: ['End'], description: t('Go to last tab', 'Aller au dernier onglet') },
      ],
    },
    {
      category: t('Forms', 'Formulaires'),
      items: [
        { keys: ['Space'], description: t('Toggle checkbox', 'Activer/désactiver case à cocher') },
        { keys: ['↑', '↓'], description: t('Navigate select options', 'Naviguer dans les options') },
        { keys: ['Enter'], description: t('Submit form', 'Soumettre le formulaire') },
      ],
    },
    {
      category: t('Help', 'Aide'),
      items: [
        { keys: ['?'], description: t('Show this help modal', 'Afficher cette aide') },
      ],
    },
  ]

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        id="keyboard-shortcuts-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="shortcuts-modal-title"
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                <Command className="h-5 w-5 text-white" aria-hidden="true" />
              </div>
              <h2 id="shortcuts-modal-title" className="text-2xl font-bold text-slate-900">
                {t('Keyboard Shortcuts', 'Raccourcis clavier')}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
              aria-label={t('Close keyboard shortcuts help', 'Fermer l\'aide des raccourcis clavier')}
            >
              <X className="h-5 w-5 text-slate-500" aria-hidden="true" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {shortcuts.map((section, sectionIndex) => (
              <div key={sectionIndex}>
                <h3 className="text-lg font-semibold text-slate-900 mb-3">{section.category}</h3>
                <div className="space-y-2">
                  {section.items.map((shortcut, itemIndex) => (
                    <div
                      key={itemIndex}
                      className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-slate-50"
                    >
                      <span className="text-slate-700">{shortcut.description}</span>
                      <div className="flex items-center gap-1">
                        {shortcut.keys.map((key, keyIndex) => (
                          <span key={keyIndex} className="inline-flex items-center gap-1">
                            <kbd className="px-2.5 py-1.5 text-xs font-semibold text-slate-800 bg-slate-100 border border-slate-300 rounded-md shadow-sm">
                              {key}
                            </kbd>
                            {keyIndex < shortcut.keys.length - 1 && (
                              <span className="text-slate-400 text-xs font-medium">+</span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-slate-200 bg-slate-50">
            <p className="text-sm text-slate-600 text-center">
              {t(
                'Press Esc or click outside to close this dialog',
                'Appuyez sur Échap ou cliquez à l\'extérieur pour fermer'
              )}
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
