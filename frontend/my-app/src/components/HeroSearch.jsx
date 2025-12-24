export default function HeroSearch({ claim, setClaim, onVerify, loading }) {
    return (
        <section className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <h2 className="text-xl font-semibold tracking-tight">
                Verify a Claim
            </h2>

            <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="Enter a factual claim to verify…"
                className="w-full h-32 rounded-xl border border-slate-300 focus:ring-4 focus:ring-emerald-200 focus:border-emerald-500 outline-none p-4 resize-none"
            />

            <div className="flex justify-end">
                <button
                    onClick={onVerify}
                    disabled={loading}
                    className="px-6 py-3 rounded-xl bg-emerald-600 text-white font-medium shadow-md hover:bg-emerald-700 transition"
                >
                    {loading ? "Verifying…" : "Verify Claim"}
                </button>
            </div>
        </section>
    );
}
