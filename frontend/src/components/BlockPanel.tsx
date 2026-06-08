import { useState } from "react";

const BLOCK_LABELS: Record<number, string> = {
  1: "Role Frame",
  2: "Global Constraints",
  3: "Recent Decisions",
  4: "Active Constraints",
  5: "Session Context",
  6: "Open Questions",
  7: "Stale Flags",
  8: "Session Boundaries",
};

const BLOCK_COLORS: Record<number, string> = {
  2: "border-red-700 bg-red-950",
  4: "border-orange-700 bg-orange-950",
  3: "border-blue-700 bg-blue-950",
  5: "border-gray-700 bg-gray-800",
  7: "border-yellow-700 bg-yellow-950",
  8: "border-green-700 bg-green-950",
};

export default function BlockPanel({ blocks, nodes }: { blocks: any; nodes: any[] }) {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-3">8-Block Structure</h2>
      <div className="space-y-2">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((blockNum) => {
          const block = blocks[blockNum];
          if (!block || (block.node_count === 0 && blockNum !== 8)) return null;

          const colorClass = BLOCK_COLORS[blockNum] || "border-gray-700 bg-gray-800";
          const isOpen = open === blockNum;
          const blockNodes = nodes.filter((n) => n.block === blockNum && !n.omitted);

          return (
            <div key={blockNum} className={`border rounded-lg overflow-hidden ${colorClass}`}>
              <button
                onClick={() => setOpen(isOpen ? null : blockNum)}
                className="w-full flex items-center justify-between px-4 py-3 text-left"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono text-gray-400">Block {blockNum}</span>
                  <span className="font-semibold text-white">{BLOCK_LABELS[blockNum]}</span>
                  <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full">
                    {blockNum === 8 ? "CAPTURE" : `${block.node_count} nodes`}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-400">{block.total_tokens} tokens</span>
                  <span className="text-gray-500">{isOpen ? "▲" : "▼"}</span>
                </div>
              </button>

              {isOpen && (
                <div className="px-4 pb-3 space-y-1 border-t border-gray-700">
                  {blockNum === 8 ? (
                    <p className="text-sm text-green-300 mt-2">CAPTURE instruction injected at session boundary.</p>
                  ) : blockNodes.length === 0 ? (
                    <p className="text-sm text-gray-500 mt-2">Empty</p>
                  ) : (
                    blockNodes.map((n) => (
                      <div key={n.id} className="flex items-center justify-between py-1 text-sm">
                        <span className="font-mono text-gray-400 w-16">{n.id}</span>
                        <span className="text-gray-300 flex-1">{n.title}</span>
                        <span className={`text-xs px-2 py-0.5 rounded font-mono ${
                          n.compression_level === "FULL" ? "bg-green-900 text-green-300" :
                          n.compression_level === "COMPRESSED" ? "bg-blue-900 text-blue-300" :
                          n.compression_level === "OMIT" ? "bg-red-900 text-red-300" :
                          "bg-gray-700 text-gray-300"
                        }`}>
                          {n.compression_level}
                        </span>
                        <span className="text-gray-500 text-xs ml-2">{n.current_tokens}t</span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}