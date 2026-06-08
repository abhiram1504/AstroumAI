export default function BudgetBar({ breakdown }: { breakdown: any }) {
  const { system_prompt_tokens, context_tokens, user_message_tokens, total, budget } = breakdown;
  const pct = (n: number) => Math.min((n / budget) * 100, 100).toFixed(1);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-semibold text-white">Token Budget</h2>
        <span className={`text-sm font-bold ${total > budget ? "text-red-400" : "text-green-400"}`}>
          {total} / {budget} {total > budget ? "⚠ OVER" : "✓ OK"}
        </span>
      </div>

      {/* Stacked bar */}
      <div className="w-full h-8 bg-gray-800 rounded-lg overflow-hidden flex mb-3">
        <div className="h-full bg-purple-600 flex items-center justify-center text-xs text-white" style={{ width: `${pct(system_prompt_tokens)}%` }}>
          {system_prompt_tokens > 50 ? `${system_prompt_tokens}` : ""}
        </div>
        <div className="h-full bg-blue-500 flex items-center justify-center text-xs text-white" style={{ width: `${pct(context_tokens)}%` }}>
          {context_tokens > 50 ? `${context_tokens}` : ""}
        </div>
        <div className="h-full bg-amber-500 flex items-center justify-center text-xs text-white" style={{ width: `${pct(user_message_tokens)}%` }}>
          {user_message_tokens > 50 ? `${user_message_tokens}` : ""}
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-purple-600" />
          <span className="text-gray-300">System Prompt: <strong>{system_prompt_tokens}</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-blue-500" />
          <span className="text-gray-300">Context: <strong>{context_tokens}</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-amber-500" />
          <span className="text-gray-300">User Reserve: <strong>{user_message_tokens}</strong></span>
        </div>
      </div>

      <div className="mt-3 text-sm text-gray-400">
        Remaining: <span className="text-green-400 font-semibold">{breakdown.remaining} tokens</span>
      </div>
    </div>
  );
}