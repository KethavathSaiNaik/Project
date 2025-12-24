export default function Navbar() {
    return (
        <nav className="sticky top-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <span className="font-semibold tracking-tight text-slate-100">
                    🧠 ClaimAI
                </span>
                <span className="text-sm text-slate-400">
                    Fact Verification
                </span>
            </div>
        </nav>
    );
}
