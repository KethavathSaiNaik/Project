import { useState } from "react";
import { askChat } from "../api/chatApi";

export default function ChatPanel({ result }) {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);

    async function handleAsk() {
        if (!question.trim()) return;

        const res = await askChat({
            query_id: result.query_id,
            question,
            label: result.label,
            confidence: result.confidence,
        });

        setMessages([
            ...messages,
            { role: "user", text: question },
            { role: "ai", text: res.answer },
        ]);

        setQuestion("");
    }

    return (
        <aside className="bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 p-6 shadow-xl flex flex-col">
            <h3 className="text-lg font-semibold mb-4">
                Explainability
            </h3>

            <div className="flex-1 space-y-3 overflow-y-auto mb-4">
                {messages.map((m, i) => (
                    <div
                        key={i}
                        className={`rounded-xl p-3 text-sm ${m.role === "user"
                            ? "bg-indigo-600/20 text-slate-100 self-end"
                            : "bg-black/40 border border-white/10 text-slate-300"
                            }`}
                    >
                        {m.role === "ai" && (
                            <span className="block text-xs font-semibold text-indigo-400 mb-1">
                                AI
                            </span>
                        )}
                        {m.text}
                    </div>
                ))}
            </div>

            <div className="flex gap-2">
                <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask why this decision was made…"
                    className="flex-1 bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm outline-none text-slate-100"
                />
                <button
                    onClick={handleAsk}
                    className="px-4 py-2 rounded-lg bg-indigo-600 text-white"
                >
                    Ask
                </button>
            </div>
        </aside>
    );
}
