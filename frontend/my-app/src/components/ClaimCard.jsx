export default function ClaimCard({ claim, setClaim, onVerify, loading }) {
    return (
        <section className="bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 p-6 shadow-xl space-y-5">
            <h2 className="text-lg font-semibold tracking-tight">
                Verify a Claim
            </h2>

            <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="Example: India won the 2024 T20 World Cup."
                className="w-full h-32 rounded-xl bg-black/40 border border-white/10 p-4 text-slate-100 placeholder-slate-400 outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />

            <div className="flex justify-end">
                <button
                    onClick={onVerify}
                    disabled={loading}
                    className="px-6 py-3 rounded-xl bg-indigo-600 text-white font-medium shadow-lg shadow-indigo-600/30 hover:-translate-y-0.5 transition"
                >
                    {loading ? "Verifying…" : "Verify Claim"}
                </button>
            </div>
        </section>
    );
}
