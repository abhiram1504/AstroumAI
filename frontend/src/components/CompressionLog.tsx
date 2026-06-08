export default function CompressionLog({ log }: { log: any[] }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-3">
        Compression Log — {log.length - 1} passes
      </h2>
      <div className="space-y-2">
        {log.map((entry, i) => (
          <div
            key={i}
            className={`flex items-start gap-3 p-3 rounded-lg text-sm ${
              entry.over_budget ? "bg-red-950 border border-red-800" : "bg-gray-800"
            }`}
          >
            <span className="text-gray-500 font-mono w-12 shrink-0">
              {entry.pass === 0 ? "START" : `Pass ${entry.pass}`}
            </span>
            <span className="text-gray-300 flex-1">{entry.action}</span>
            <span className={`font-mono shrink-0 ${entry.over_budget ? "text-red-400" : "text-green-400"}`}>
              {entry.total_tokens} tok
            </span>
            {entry.tokens_saved > 0 && (
              <span className="text-amber-400 font-mono shrink-0">-{entry.tokens_saved}</span>
            )}
          </div>
        ))}
      </div>
      {log.length === 1 && (
        <p className="text-gray-500 text-sm mt-2">
          No compression needed — try lowering the budget slider to see compression in action.
        </p>
      )}
    </div>
  );
}