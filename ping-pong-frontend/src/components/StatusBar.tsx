export default function StatusBar({status}: { status: { colored_pixels: number, total_pixels: number, done: boolean } }) {
  const progress = status.total_pixels>0 ? status.colored_pixels/status.total_pixels*100 : 0;
  return (
    <div>
      <progress value={progress} max={100}></progress>
      {Math.round(progress)}%
    </div>
  )
}
