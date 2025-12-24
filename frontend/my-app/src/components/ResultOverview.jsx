export default function ResultOverview({ result }) {
    const labelMap = {
        SUPPORTS: { text: "SUPPORTED", color: "text-emerald-400" },
        REFUTES: { text: "REFUTED", color: "text-rose-400" },
        NOT_ENOUGH_INFO: { text: "NOT ENOUGH INFO", color: "text-amber-400" },
    };

    const { text, color } = labelMap[result.label];

    return (
        <section className="bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between">
                <span className={`text-sm font-semibold ${color}`}>
                    {text}
                </span>
                <span className="text-2xl font-bold">
                    {(result.confidence * 100).toFixed(1)}%
                </span>
            </div>

            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                <div
                    className="h-2 bg-gradient-to-r from-indigo-400 to-cyan-400"
                    style={{ width: `${result.confidence * 100}%` }}
                />
            </div>
        </section>
    );
}
