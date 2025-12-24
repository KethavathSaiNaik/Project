import { useState } from "react";
import { verifyClaim } from "../api/verifyApi";
import Navbar from "../components/Navbar";
import Header from "../components/Header";
import ClaimCard from "../components/ClaimCard";
import ResultOverview from "../components/ResultOverview";
import EvidenceFeed from "../components/EvidenceFeed";
import ChatPanel from "../components/ChatPanel";

export default function VerifyPage() {
    const [claim, setClaim] = useState("");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    async function handleVerify() {
        if (!claim.trim()) return;
        setLoading(true);
        setResult(null);

        const data = await verifyClaim(claim);
        setResult(data);
        setLoading(false);
    }

    return (
        <div className="min-h-screen bg-[#FFFFFF] text-slate-100">
            <Navbar />
            <Header />

            <main className="max-w-7xl mx-auto px-6 py-12 space-y-16">
                {/* Claim + Result Row */}
                <section className="flex flex-row flex-wrap justify-center gap-6">
                    <div className="w-full md:w-1/2 max-w-xl">
                        <ClaimCard
                            claim={claim}
                            setClaim={setClaim}
                            onVerify={handleVerify}
                            loading={loading}
                        />
                    </div>

                    {result && (
                        <div className="w-full md:w-1/2 max-w-xl">
                            <ResultOverview result={result} />
                        </div>
                    )}
                </section>

                {/* Evidence + Chat Grid */}
                {result && (
                    <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2">
                            <EvidenceFeed evidence={result.evidence} />
                        </div>
                        <ChatPanel result={result} />
                    </section>
                )}
            </main>
        </div>
    );
}
