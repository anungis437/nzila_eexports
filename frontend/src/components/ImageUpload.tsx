import { useState, useCallback } from 'react'
import { Upload, X, Image as ImageIcon, AlertCircle } from 'lucide-react'
import api from '../lib/api'
import { useMutation, useQueryClient } from '@tanstack/react-query'

interface ImageUploadProps {
  vehicleId: number
  onUploadComplete?: () => void
}

export default function ImageUpload({ vehicleId, onUploadComplete }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadQueue, setUploadQueue] = useState<File[]>([])
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('image', file)
      
      const response = await api.post(`/vehicles/${vehicleId}/upload_image/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicle', vehicleId] })
      onUploadComplete?.()
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Failed to upload image')
    },
  })

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    setError(null)

    const files = Array.from(e.dataTransfer.files).filter(file =>
      file.type.startsWith('image/')
    )

    if (files.length === 0) {
      setError('Please drop image files only')
      return
    }

    if (files.length > 10) {
      setError('Maximum 10 images can be uploaded at once')
      return
    }

    setUploadQueue(files)
    files.forEach(file => uploadMutation.mutate(file))
  }, [uploadMutation])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null)
    const files = Array.from(e.target.files || []).filter(file =>
      file.type.startsWith('image/')
    )

    if (files.length === 0) {
      setError('Please select image files only')
      return
    }

    if (files.length > 10) {
      setError('Maximum 10 images can be uploaded at once')
      return
    }

    setUploadQueue(files)
    files.forEach(file => uploadMutation.mutate(file))
  }, [uploadMutation])

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploadMutation.isPending ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <div className="flex flex-col items-center gap-4">
          <div className={`
            p-4 rounded-full transition-colors
            ${isDragging ? 'bg-blue-100' : 'bg-gray-100'}
          `}>
            <Upload className={`w-8 h-8 ${isDragging ? 'text-blue-600' : 'text-gray-400'}`} />
          </div>

          <div>
            <p className="text-lg font-medium text-gray-700 mb-1">
              {isDragging ? 'Drop images here' : 'Drag & drop images here'}
            </p>
            <p className="text-sm text-gray-500">
              or{' '}
              <label className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium">
                browse files
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  disabled={uploadMutation.isPending}
                />
              </label>
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-500">
            <ImageIcon className="w-4 h-4" />
            <span>Supports: JPG, PNG, WEBP (Max 10 images, 5MB each)</span>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-700 hover:text-red-800"
            aria-label="Dismiss error"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Upload Queue */}
      {uploadQueue.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Uploading {uploadQueue.length} image(s)...</h4>
          <div className="space-y-1">
            {uploadQueue.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
              >
                <ImageIcon className="w-5 h-5 text-gray-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-700 truncate">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                {uploadMutation.isPending && (
                  <div className="flex-shrink-0">
                    <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Success Message */}
      {uploadMutation.isSuccess && !uploadMutation.isPending && (
        <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <p className="text-sm">Images uploaded successfully!</p>
        </div>
      )}
    </div>
  )
}
