import { useState, useEffect } from "react";
import ConfigForm from "./components/ConfigForm";
import ImageCanvas from "./components/ImageCanvas";
import StatusBar from "./components/StatusBar";
import { validateUniqueColors } from "./utils/validateImage";
import type { Pixel } from "./types";
 

export default function App() {
  const [pixels, setPixels] = useState<Record<string, Pixel>>({});
  const [status, setStatus] = useState({ colored_pixels: 0, total_pixels: 0, done: false });
  const [dimensions, setDimensions] = useState({ m: 0, n: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [validationResult, setValidationResult] = useState<string | null>(null);

  const fetchStatus = async () => {
  try {
    const res = await fetch(`http://localhost:8000/api/status/?m=${dimensions.m}&n=${dimensions.n}`);
    const statusData = await res.json();
    setStatus(statusData);
    
    const totalPixels = dimensions.m * dimensions.n;
    
    // Get image data from backend (no pagination)
    const imgRes = await fetch(`http://localhost:8000/api/ui/?m=${dimensions.m}&n=${dimensions.n}`);
    const data = await imgRes.json();
    
    // Convert image array to pixel dictionary
    const img: Record<string, Pixel> = {};
    data.image.forEach((p: Pixel) => { 
      img[`${p.x},${p.y}`] = p 
    });
    
    setPixels(img);
    
    // Validate colors for all grid sizes
    if (statusData.done && Object.keys(img).length > 0) {
      let pixelsToValidate = img;
      let sampleNote = "";
      
      // For very large grids, validate a sample to avoid browser crashes
      if (totalPixels > 100000) {
        const sampleSize = 10000;
        const pixelEntries = Object.entries(img).slice(0, sampleSize);
        pixelsToValidate = Object.fromEntries(pixelEntries);
        sampleNote = ` (sample of ${sampleSize}/${Object.keys(img).length} pixels)`;
        console.log(`🔍 Validating sample: ${sampleSize} pixels out of ${totalPixels}`);
      }
      
      const validation = validateUniqueColors(pixelsToValidate);
      
      setValidationResult(
        validation.isValid 
          ? `✅ All pixels have unique colors${sampleNote}` 
          : `❌ Found ${validation.duplicateColors.length} duplicate colors${sampleNote}`
      );
    } else if (!statusData.done) {
      setValidationResult(null); // Clear validation while in progress
    }
    
  } catch (error) {
    console.error("Failed to fetch status:", error);
    setIsLoading(false);
    setValidationResult("❌ Error fetching data");
  }
};

  useEffect(() => {
    if (isLoading && !status.done) {
      console.log('🔄 Starting polling...');
      fetchStatus();
      const interval = setInterval(fetchStatus, 500);
      return () => {
        console.log('⏹️ Stopping polling...');
        clearInterval(interval);
      };
    }
  }, [isLoading, status.done, dimensions]);

  const handleReset = () => {
    setPixels({});
    setStatus({ colored_pixels: 0, total_pixels: 0, done: false });
    setDimensions({ m: 0, n: 0 });
    setValidationResult(null); // Clear validation result
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingTop: '20px' }}>
      <div style={{ padding: '0px 40px', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
        <h1 style={{ margin: '0 0 40px 0', textAlign: 'center' }}>Random Pixel Ping-Pong</h1>
        <div style={{ display: 'flex', flexDirection: 'row', gap: '20px', width: '100%', maxWidth: '1200px', justifyContent: 'center' }}>
          <div style={{ flex: 1, minWidth: '300px' }}>
            <ConfigForm setIsLoading={setIsLoading} onReset={handleReset} setDimensions={setDimensions} />
            <StatusBar status={status} />
            {validationResult && (
              <div style={{
                padding: '10px',
                margin: '20px 0',
                borderRadius: '4px',
                fontSize: '14px',
                fontWeight: 'bold',
                backgroundColor: validationResult.includes('✅') ? '#d4edda' : '#f8d7da',
                color: validationResult.includes('✅') ? '#155724' : '#721c24',
                border: `1px solid ${validationResult.includes('✅') ? '#c3e6cb' : '#f5c6cb'}`
              }}>
                {validationResult}
              </div>
            )}
          </div>
          <div style={{ flex: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
              <div style={{ writingMode: 'vertical-rl', textOrientation: 'mixed', paddingRight: '10px' }}>
                Y: {dimensions.m}
              </div>
              <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <ImageCanvas pixels={pixels} m={dimensions.m} n={dimensions.n}/>
                <div style={{ position: 'absolute', bottom: '-25px', left: '0', right: '0', textAlign: 'center' }}>
                  X: {dimensions.n}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
