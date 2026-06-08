"use client";
import { useState } from "react";
import BudgetBar from "@/components/BudgetBar";
import CompressionLog from "@/components/CompressionLog";
import BlockPanel from "@/components/BlockPanel";
import NodeCard from "@/components/NodeCard";
import BudgetSlider from "@/components/BudgetSlider";
import ContextViewer from "@/components/ContextViewer";

const USERS = [
  { id: "U-VIKRAM", name: "Dr. Vikram (HOD Ortho)" },
  { id: "U-PRIYA", name: "Nurse Priya" },
];

const PATIENTS = [
  { id: "PAT-RAJAN", name: "Mr. Rajan" },
  { id: "PAT-PADMA", name: "Mrs. Padma" },
];

export default function Home() {
  const [userId, setUserId] = useState("U-VIKRAM");
  const [patientId, setPatientId] = useState("PAT-RAJAN");
  const [tokenBudget, setTokenBudget] = useState(4000);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showContext, setShowContext] = useState(false);

  async function compose() {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/compose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, patient_id: patientId, token_budget: tokenBudget }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      alert("Backend not reachable. Make sure uvicorn is running.");
    }
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">BRAHMO Composition Agent</h1>
          <p className="text-gray-400 mt-1">Token Budget + 8-Block Assembly + Iterative Compression</p>
        </div>

        {/* Controls */}
        <div className="bg-gray-900 rounded-xl p-6 mb-6 border border-gray-800">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">User</label>
              <select
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              >
                {USERS.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Patient</label>
              <select
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
              >
                {PATIENTS.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Token Budget</label>
              <BudgetSlider value={tokenBudget} onChange={setTokenBudget} />
            </div>
          </div>

          <button
            onClick={compose}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {loading ? "Composing..." : "Compose Context"}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">

            {/* Stats row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Nodes Included", value: result.stats.nodes_included },
                { label: "Nodes Omitted", value: result.stats.nodes_omitted },
                { label: "Constraints Protected", value: result.stats.constraints_protected },
                { label: "Compression Passes", value: result.stats.compression_passes },
              ].map((s) => (
                <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-white">{s.value}</div>
                  <div className="text-sm text-gray-400 mt-1">{s.label}</div>
                </div>
              ))}
            </div>

            {/* Budget error warning */}
            {result.stats.budget_error && (
              <div className="bg-red-900 border border-red-700 rounded-xl p-4 text-red-200">
                ⚠️ <strong>Budget Error:</strong> CONSTRAINTs alone exceed the token budget.
                Cannot compress safety-critical nodes. Increase budget or review CONSTRAINT set.
              </div>
            )}

            {/* Token budget bar */}
            <BudgetBar breakdown={result.token_breakdown} />

            {/* Compression log */}
            <CompressionLog log={result.compression_log} />

            {/* Block panel */}
            <BlockPanel blocks={result.metadata.block_summary} nodes={result.metadata.node_details} />

            {/* Node cards */}
            <div>
              <h2 className="text-lg font-semibold text-white mb-3">Per-Node Detail</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.metadata.node_details.map((node: any) => (
                  <NodeCard key={node.id} node={node} />
                ))}
              </div>
            </div>

            {/* View context button */}
            <button
              onClick={() => setShowContext(true)}
              className="w-full bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white font-semibold py-3 rounded-lg transition-colors"
            >
              View Final Context String
            </button>

          </div>
        )}
      </div>

      {/* Context modal */}
      {showContext && result && (
        <ContextViewer
          contextString={result.context_string}
          onClose={() => setShowContext(false)}
        />
      )}
    </main>
  );
}