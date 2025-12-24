export default function EvidenceFeed({ evidence }) {
    return (
        <section className="bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 p-6 shadow-xl space-y-6 m-4">
            <h3 className="text-lg font-semibold tracking-tight">
                Supporting Evidence
            </h3>

            {evidence.map((ev, i) => (
                <article
                    key={i}
                    className="bg-black/40 border border-white/10 rounded-xl p-5 space-y-3"
                >
                    <h4 className="font-medium text-slate-100">
                        {ev.title}
                    </h4>

                    <p className="text-sm text-slate-400">
                        Source: {ev.source}
                    </p>

                    <blockquote className="border-l-4 border-indigo-500 pl-4 text-slate-300 italic">
                        {ev.sentence_text}
                    </blockquote>

                    <a
                        href={ev.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm text-indigo-400 hover:underline"
                    >
                        View Source →
                    </a>
                </article>
            ))}
        </section>
    );
}
