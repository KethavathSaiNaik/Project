export default function ClaimInput({ claim, setClaim, onVerify }) {
    return (
        <div className="bg-slate-900/80 backdrop-blur rounded-2xl p-6 shadow-xl space-y-4">
            <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="Example: India won the 2024 T20 World Cup."
                className="w-full h-32 p-4 rounded-xl bg-slate-800 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 outline-none"
            />

            <button
                onClick={onVerify}
                className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 transition-all font-semibold text-lg"
            >
                🔍 Verify Claim
            </button>
        </div>
    );
}
