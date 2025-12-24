export default function Header() {
    return (
        <header className="sticky top-14 z-40 bg-black/20 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-6 py-10">
                <h1 className="text-4xl font-extrabold tracking-tight">
                    AI Claim Verification
                </h1>
                <p className="text-slate-400 mt-2 max-w-2xl">
                    Validate claims using evidence retrieval and DeBERTa-based NLI.
                </p>
            </div>
        </header>
    );
}
