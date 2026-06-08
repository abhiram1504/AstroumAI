export default function ContextViewer({ contextString, onClose }: { contextString: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-3xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Final Context String</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl">✕</button>
        </div>
        <pre className="p-4 overflow-auto text-sm text-gray-300 whitespace-pre-wrap font-mono flex-1">
          {contextString}
        </pre>
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={() => navigator.clipboard.writeText(contextString)}
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm"
          >
            Copy to Clipboard
          </button>
        </div>
      </div>
    </div>
  );
}