const TYPE_COLORS: Record<string, string> = {
  CONSTRAINT: "bg-red-900 text-red-300 border-red-700",
  DECISION: "bg-blue-900 text-blue-300 border-blue-700",
  ANTI_PATTERN: "bg-orange-900 text-orange-300 border-orange-700",
  FACT: "bg-gray-800 text-gray-300 border-gray-600",
};

const LEVEL_COLORS: Record<string, string> = {
  FULL: "text-green-400",
  COMPRESSED: "text-blue-400",
  CONSTRAINT_ONLY: "text-amber-400",
  OMIT: "text-red-400",
};

export default function NodeCard({ node }: { node: any }) {
  return (
    <div className={`rounded-xl border p-4 ${node.omitted ? "opacity-40" : ""} ${TYPE_COLORS[node.type] || "bg-gray-800 border-gray-600"}`}>
      <div className="flex items-start justify-between mb-2">
        <div>
          <span className="font-mono text-xs opacity-70">{node.id}</span>
          <h3 className="font-semibold text-white text-sm">{node.title}</h3>
        </div>
        <span className={`text-xs font-bold ${LEVEL_COLORS[node.compression_level]}`}>
          {node.compression_level}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mt-2">
        <div className="flex justify-between">
          <span className="opacity-60">Retrieval</span>
          <span className="font-mono">{node.retrieval_weight.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-60">Injection</span>
          <span className="font-mono">{node.injection_weight.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-60">Distance</span>
          <span className="font-mono">{node.distance}</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-60">Block</span>
          <span className="font-mono">{node.block}</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-60">Tokens</span>
          <span className="font-mono">{node.current_tokens}</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-60">Zone</span>
          <span className="font-mono">{node.zone}</span>
        </div>
      </div>

      <p className="text-xs opacity-50 mt-2 italic">{node.reason}</p>

      {node.status === "REVIEW_REQUIRED" && (
        <div className="mt-2 text-xs bg-yellow-900 text-yellow-300 px-2 py-1 rounded">
          ⚠ STALE — Review Required
        </div>
      )}
    </div>
  );
}