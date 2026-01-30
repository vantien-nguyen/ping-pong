import { useRef, useEffect } from "react";
import type { Pixel } from "../types";

interface ImageCanvasProps {
  pixels: Record<string, Pixel>;
  m: number;
  n: number;
}

const ImageCanvas = ({ pixels, m, n }: ImageCanvasProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate pixel size - make sure pixels are visible!
    const maxCanvasSize = 600;
    const pixelSize = Math.max(2, Math.min(10, maxCanvasSize / Math.max(m, n))); // Min 2px
    
    // Set canvas dimensions
    canvas.width = n * pixelSize;
    canvas.height = m * pixelSize;
    
    console.log(`🎨 Canvas: ${canvas.width}x${canvas.height}, Pixel size: ${pixelSize}px`);
    console.log(`🖼️ Rendering ${Object.keys(pixels).length} pixels`);
    
    // Draw all pixels - no limits!
    Object.values(pixels).forEach((pixel, index) => {
      ctx.fillStyle = `rgb(${pixel.color[0]}, ${pixel.color[1]}, ${pixel.color[2]})`;
      ctx.fillRect(pixel.x * pixelSize, pixel.y * pixelSize, pixelSize, pixelSize);
    });
    
    // Draw grid lines for debugging (optional)
    ctx.strokeStyle = 'rgba(200, 200, 200, 0.2)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= n; i++) {
      ctx.beginPath();
      ctx.moveTo(i * pixelSize, 0);
      ctx.lineTo(i * pixelSize, canvas.height);
      ctx.stroke();
    }
    for (let i = 0; i <= m; i++) {
      ctx.beginPath();
      ctx.moveTo(0, i * pixelSize);
      ctx.lineTo(canvas.width, i * pixelSize);
      ctx.stroke();
    }
    
  }, [pixels, m, n]);
  
  return (
    <div>
      <canvas 
        ref={canvasRef}
        style={{ 
          border: '1px solid #ccc',
          imageRendering: 'pixelated', // Sharp pixels
          maxWidth: '100%',
          height: 'auto',
          backgroundColor: '#f0f0f0'
        }}
      />
      <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
        Pixels: {Object.keys(pixels).length} / {m * n} | Grid: {m}×{n}
      </div>
    </div>
  );
};

export default ImageCanvas;
