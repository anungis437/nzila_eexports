import React, { useState } from 'react';
import { Play, Clock } from 'lucide-react';
import VideoPlayer from './VideoPlayer';

interface Video {
  id: number;
  video: string;
  thumbnail?: string;
  caption?: string;
  duration_seconds?: number;
  created_at: string;
}

interface VideoGalleryProps {
  videos: Video[];
  className?: string;
}

const VideoGallery: React.FC<VideoGalleryProps> = ({ videos, className = '' }) => {
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return '';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (videos.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Play className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>No video walkarounds available yet</p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Video Player Modal */}
      {selectedVideo && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedVideo(null)}
        >
          <div 
            className="relative max-w-4xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              onClick={() => setSelectedVideo(null)}
              className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors"
            >
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Video Player */}
            <VideoPlayer
              videoUrl={selectedVideo.video}
              thumbnail={selectedVideo.thumbnail}
              title={selectedVideo.caption}
              autoPlay={true}
            />

            {/* Video Info */}
            {selectedVideo.caption && (
              <div className="mt-4 text-white">
                <p className="text-sm text-gray-300">
                  {new Date(selectedVideo.created_at).toLocaleDateString()}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Video Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {videos.map((video) => (
          <div
            key={video.id}
            className="group relative bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:shadow-lg transition-all"
            onClick={() => setSelectedVideo(video)}
          >
            {/* Thumbnail */}
            <div className="relative aspect-video bg-gray-200">
              {video.thumbnail ? (
                <img
                  src={video.thumbnail}
                  alt={video.caption || 'Video thumbnail'}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Play className="w-12 h-12 text-gray-400" />
                </div>
              )}

              {/* Play Button Overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all flex items-center justify-center">
                <div className="bg-white bg-opacity-90 rounded-full p-3 opacity-0 group-hover:opacity-100 transform scale-90 group-hover:scale-100 transition-all">
                  <Play className="w-6 h-6 text-gray-900" fill="currentColor" />
                </div>
              </div>

              {/* Duration Badge */}
              {video.duration_seconds && (
                <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{formatDuration(video.duration_seconds)}</span>
                </div>
              )}
            </div>

            {/* Caption */}
            {video.caption && (
              <div className="p-3">
                <p className="text-sm text-gray-700 line-clamp-2">{video.caption}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default VideoGallery;
