export default function BudgetSlider({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>1000</span>
        <span className="text-white font-semibold">{value} tokens</span>
        <span>6000</span>
      </div>
      <input
        type="range"
        min={1000}
        max={6000}
        step={100}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-blue-500"
      />
    </div>
  );
}