import React, { useState, useRef, useCallback } from 'react';

interface CameraProps {
  onPhotoCapture: (photoData: string, photoBlob: Blob) => void;
  onClose: () => void;
}

const Camera: React.FC<CameraProps> = ({ onPhotoCapture, onClose }) => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedPhoto, setCapturedPhoto] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const startCamera = useCallback(async () => {
    try {
      setError(null);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });

      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      setError('Camera access denied or unavailable');
      console.error('Camera error:', err);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  }, [stream]);

  const capturePhoto = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (context) {
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw current video frame to canvas
        context.drawImage(video, 0, 0);

        // Convert to base64 data URL
        const photoData = canvas.toDataURL('image/jpeg', 0.8);

        // Also create blob for file storage
        canvas.toBlob((blob) => {
          if (blob) {
            onPhotoCapture(photoData, blob);
            setCapturedPhoto(photoData);
          }
        }, 'image/jpeg', 0.8);
      }
    }
  }, [onPhotoCapture]);

  const retakePhoto = useCallback(() => {
    setCapturedPhoto(null);
  }, []);

  const confirmPhoto = useCallback(() => {
    if (capturedPhoto) {
      stopCamera();
      onClose();
    }
  }, [capturedPhoto, stopCamera, onClose]);

  React.useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, [startCamera, stopCamera]);

  if (error) {
    return (
      <div className="camera-modal">
        <div className="camera-container">
          <div className="camera-error">
            <p>📷 {error}</p>
            <button onClick={onClose} className="close-button">
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="camera-modal">
      <div className="camera-container">
        {!capturedPhoto ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="camera-video"
            />
            <canvas
              ref={canvasRef}
              style={{ display: 'none' }}
            />

            <div className="camera-controls">
              <button onClick={onClose} className="camera-cancel">
                Cancel
              </button>
              <button onClick={capturePhoto} className="camera-capture">
                📷 Capture
              </button>
            </div>
          </>
        ) : (
          <>
            <img
              src={capturedPhoto}
              alt="Captured"
              className="captured-photo"
            />

            <div className="photo-controls">
              <button onClick={retakePhoto} className="photo-retake">
                🔄 Retake
              </button>
              <button onClick={confirmPhoto} className="photo-confirm">
                ✅ Use Photo
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Camera;