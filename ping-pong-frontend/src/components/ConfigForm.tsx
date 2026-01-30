import { useState } from "react";

interface Props {
  setIsLoading: (isLoading: boolean) => void;
  onReset: () => void;
  setDimensions: (dimensions: { m: number; n: number }) => void;
}

export default function ConfigForm({ setIsLoading, onReset, setDimensions }: Props) {
  const [m, setM] = useState(5);
  const [n, setN] = useState(5);

  const submit = async () => {
    const M = m > 0 ? m : 1;
    const N = n > 0 ? n : 1;
    
    onReset();
    setIsLoading(true);
    setDimensions({ m: M, n: N });
    
    try {
      // Configure the grid
      await fetch("http://localhost:8000/api/configure/", {
        method: "POST", 
        headers: {"Content-Type":"application/json"}, 
        body: JSON.stringify({m: M, n: N})
      });
      
      // Start generation with proper headers and body
      await fetch("http://localhost:8000/api/generate/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({m: M, n: N})
      });
    } catch (error) {
      console.error("Failed to start generation:", error);
      setIsLoading(false);
    }
  }

  const handleInputChange = (size: 'm' | 'n', value: string) => {
    // Allow empty string during editing, or convert to number if not empty
    if (value === '') {
      if (size === 'm') {
        setM(0); // Temporarily set to 0 to allow empty input
      } else {
        setN(0);
      }
    } else {
      const numValue = Number(value);
      if (size === 'm') {
        setM(numValue > 0 ? numValue : 1);
      } else {
        setN(numValue > 0 ? numValue : 1);
      }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '10px' }}>
        <input 
          type="number" 
          value={m === 0 ? '' : m} 
          onChange={e=>handleInputChange('m', e.target.value)}
          onBlur={() => {
            if (m === 0) setM(1);
          }}
        /> 
        <span>m</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '10px' }}>
        <input 
          type="number" 
          value={n === 0 ? '' : n} 
          onChange={e=>handleInputChange('n', e.target.value)}
          onBlur={() => {
            if (n === 0) setN(1);
          }}
        /> 
        <span>n</span>
      </div>
      <button style={{ width: '50%', margin: '10px 0 20px', backgroundColor: '#007bff', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', transition: 'background-color 0.2s' }} 
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#0056b3'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#007bff'}
        onClick={submit}>Start</button>
    </div>
  )
}
