
import type { Pixel } from "../types";

/**
 * Converts color to string format for comparison
 */
function colorToString(color: string | [number, number, number]): string {
  if (Array.isArray(color)) {
    return `rgb(${color[0]},${color[1]},${color[2]})`;
  }
  return color;
}

/**
 * Validates if all pixels in the image have unique colors
 * @param pixels - Record of pixels with string keys
 * @returns Object with validation result and details
 */
export function validateUniqueColors(pixels: Record<string, Pixel>): {
  isValid: boolean;
  totalPixels: number;
  duplicateColors: string[];
} {
  const pixelArray = Object.values(pixels);
  const colorMap = new Map<string, Array<{ x: number; y: number }>>();
  
  // Group pixels by color
  pixelArray.forEach((pixel) => {
    const colorStr = colorToString(pixel.color);
    if (!colorMap.has(colorStr)) {
      colorMap.set(colorStr, []);
    }
    colorMap.get(colorStr)!.push({ x: pixel.x, y: pixel.y });
  });
  
  // Find duplicate colors
  const duplicateColors: string[] = [];
  
  colorMap.forEach((positions, color) => {
    if (positions.length > 1) {
      duplicateColors.push(color);
    }
  });
  
  
  return {
    isValid: duplicateColors.length === 0,
    totalPixels: pixelArray.length,
    duplicateColors,
  };
}
