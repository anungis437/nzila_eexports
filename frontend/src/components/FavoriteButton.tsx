import { Heart } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

interface FavoriteButtonProps {
  vehicleId: number
  className?: string
  showLabel?: boolean
}

export default function FavoriteButton({ vehicleId, className = '', showLabel = false }: FavoriteButtonProps) {
  const { user } = useAuth()
  const queryClient = useQueryClient()

  // Check if vehicle is favorited
  const { data: isFavorited } = useQuery({
    queryKey: ['favorite-check', vehicleId],
    queryFn: async () => {
      if (!user) return false
      try {
        const response = await api.get(`/favorites/check/${vehicleId}/`)
        return response.data.is_favorited
      } catch {
        return false
      }
    },
    enabled: !!user,
  })

  // Toggle favorite mutation
  const toggleMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/favorites/toggle/', { vehicle: vehicleId })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorite-check', vehicleId] })
      queryClient.invalidateQueries({ queryKey: ['favorites'] })
    },
  })

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!user) {
      alert('Please sign in to add favorites')
      return
    }
    toggleMutation.mutate()
  }

  if (!user) return null

  return (
    <button
      onClick={handleClick}
      disabled={toggleMutation.isPending}
      className={`
        flex items-center gap-2 p-2 rounded-lg transition-all
        ${isFavorited 
          ? 'text-red-500 hover:text-red-600 bg-red-50' 
          : 'text-gray-400 hover:text-red-500 hover:bg-red-50'
        }
        ${toggleMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
    >
      <Heart 
        className={`w-5 h-5 transition-all ${isFavorited ? 'fill-current' : ''}`}
      />
      {showLabel && (
        <span className="text-sm font-medium">
          {isFavorited ? 'Saved' : 'Save'}
        </span>
      )}
    </button>
  )
}
