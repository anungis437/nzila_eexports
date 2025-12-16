import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, X, Check, Package, DollarSign, Car, FileText, TrendingUp } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../lib/api'

interface Notification {
  id: number
  type: 'lead' | 'deal' | 'commission' | 'shipment' | 'vehicle' | 'document' | 'system'
  title: string
  message: string
  is_read: boolean
  link?: string
  created_at: string
}

export default function NotificationBell() {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Fetch notifications
  const { data: notificationsData, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await api.getNotifications({ limit: 20 })
      return response
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const notifications: Notification[] = notificationsData?.notifications || []
  const unreadCount = notificationsData?.unread_count || 0

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (id: number) => {
      return await api.markNotificationRead(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      return await api.markAllNotificationsRead()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const getNotificationIcon = (type: Notification['type']) => {
    const iconClass = 'w-5 h-5'
    switch (type) {
      case 'lead':
        return <TrendingUp className={iconClass} />
      case 'deal':
        return <FileText className={iconClass} />
      case 'commission':
        return <DollarSign className={iconClass} />
      case 'shipment':
        return <Package className={iconClass} />
      case 'vehicle':
        return <Car className={iconClass} />
      case 'document':
        return <FileText className={iconClass} />
      default:
        return <Bell className={iconClass} />
    }
  }

  const getNotificationColor = (type: Notification['type']) => {
    switch (type) {
      case 'lead':
        return 'from-blue-500 to-indigo-600'
      case 'deal':
        return 'from-green-500 to-emerald-600'
      case 'commission':
        return 'from-amber-500 to-orange-600'
      case 'shipment':
        return 'from-purple-500 to-pink-600'
      case 'vehicle':
        return 'from-slate-500 to-slate-600'
      case 'document':
        return 'from-red-500 to-rose-600'
      default:
        return 'from-slate-500 to-slate-600'
    }
  }

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id)
    }
    if (notification.link) {
      window.location.href = notification.link
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
            <h3 className="text-lg font-semibold text-slate-900">
              {language === 'fr' ? 'Notifications' : 'Notifications'}
            </h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllAsReadMutation.mutate()}
                  disabled={markAllAsReadMutation.isPending}
                  className="text-xs text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
                >
                  {language === 'fr' ? 'Tout marquer comme lu' : 'Mark all read'}
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-white/50 rounded transition-colors"
              >
                <X className="w-5 h-5 text-slate-600" />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="max-h-[480px] overflow-y-auto">
            {isLoading ? (
              <div className="p-4 space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="flex gap-3">
                      <div className="w-10 h-10 bg-slate-200 rounded-lg" />
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-slate-200 rounded w-3/4" />
                        <div className="h-3 bg-slate-200 rounded w-full" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-500">
                  {language === 'fr' ? 'Aucune notification' : 'No notifications'}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`p-4 hover:bg-slate-50 transition-colors cursor-pointer ${
                      !notification.is_read ? 'bg-blue-50/50' : ''
                    }`}
                  >
                    <div className="flex gap-3">
                      {/* Icon */}
                      <div
                        className={`w-10 h-10 rounded-lg bg-gradient-to-br ${getNotificationColor(
                          notification.type
                        )} flex items-center justify-center text-white flex-shrink-0`}
                      >
                        {getNotificationIcon(notification.type)}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h4 className="font-semibold text-slate-900 text-sm">{notification.title}</h4>
                          {!notification.is_read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1" />
                          )}
                        </div>
                        <p className="text-sm text-slate-600 mb-2 line-clamp-2">{notification.message}</p>
                        <p className="text-xs text-slate-400">
                          {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                        </p>
                      </div>

                      {/* Mark as read button */}
                      {!notification.is_read && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            markAsReadMutation.mutate(notification.id)
                          }}
                          className="p-1.5 hover:bg-blue-100 rounded text-blue-600 transition-colors flex-shrink-0"
                          title={language === 'fr' ? 'Marquer comme lu' : 'Mark as read'}
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-3 border-t border-slate-200 bg-slate-50">
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium w-full text-center">
                {language === 'fr' ? 'Voir toutes les notifications' : 'View all notifications'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
