export default function ConfidenceBar({ confidence }) {
    return (
        <div className="flex flex-col gap-2">
            <div className="flex justify-between text-sm text-slate-400">
                <span>Confidence</span>
                <span>{confidence.toFixed(4)}</span>
            </div>

            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                <div
                    className="h-2 bg-gradient-to-r from-emerald-400 to-cyan-400"
                    style={{ width: `${Math.min(confidence * 100, 100)}%` }}
                />
            </div>
        </div>
    );
}
