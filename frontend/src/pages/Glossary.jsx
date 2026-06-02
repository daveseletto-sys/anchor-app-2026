import React, { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import { Input } from "../components/ui/input";
import { Search, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";

const Glossary = () => {
    const [items, setItems] = useState([]);
    const [q, setQ] = useState("");

    useEffect(() => {
        api.get("/glossary").then((r) => setItems(r.data.items || []));
    }, []);

    const filtered = useMemo(() => {
        const needle = q.trim().toLowerCase();
        if (!needle) return items;
        return items.filter(
            (i) => i.term.toLowerCase().includes(needle) || i.definition.toLowerCase().includes(needle)
        );
    }, [items, q]);

    const grouped = useMemo(() => {
        const map = {};
        filtered.forEach((i) => {
            const k = i.term[0].toUpperCase();
            if (!map[k]) map[k] = [];
            map[k].push(i);
        });
        Object.keys(map).forEach((k) => map[k].sort((a, b) => a.term.localeCompare(b.term)));
        return Object.keys(map).sort().map((k) => [k, map[k]]);
    }, [filtered]);

    return (
        <div className="max-w-3xl mx-auto fade-up" data-testid="glossary-root">
            <div className="label-eyebrow">Glossary</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Recovery, in plain words.</h1>

            <div className="relative mt-8">
                <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" strokeWidth={1.5} />
                <Input
                    data-testid="glossary-search"
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    placeholder="Search terms…"
                    className="pl-10 h-12 rounded-full"
                />
            </div>

            <div className="mt-10 space-y-10">
                {grouped.map(([letter, list]) => (
                    <section key={letter} data-testid={`glossary-letter-${letter}`}>
                        <div className="sticky top-0 bg-background/95 backdrop-blur py-2 mb-3 z-10">
                            <div className="font-display text-2xl text-muted-foreground">{letter}</div>
                        </div>
                        <div className="space-y-4">
                            {list.map((it) => (
                                <div key={it.term} className="border-b border-border pb-4 last:border-0" data-testid={`glossary-term-${it.term}`}>
                                    <div className="font-display font-medium tracking-tight">{it.term}</div>
                                    <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{it.definition}</p>
                                    {it.source_name && (
                                        <a
                                            href={it.source_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-xs text-primary hover:underline inline-flex items-center gap-1 mt-2"
                                            data-testid={`glossary-source-${it.term}`}
                                        >
                                            Source: {it.source_name} <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                                        </a>
                                    )}
                                </div>
                            ))}
                        </div>
                    </section>
                ))}
                {grouped.length === 0 && <div className="text-sm text-muted-foreground">No matches.</div>}
            </div>

            <div className="mt-12 pt-6 border-t border-border">
                <Link to="/sources" className="text-sm text-primary hover:underline inline-flex items-center gap-1" data-testid="glossary-all-sources-link">
                    View reference sources <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                </Link>
                <p className="text-xs text-muted-foreground mt-2 max-w-xl">
                    Anchor is a personal wellness journal — not a medical app and not a substitute for medical advice. The glossary below points to publicly available information so you can read more if you're curious. Always speak with your own doctor about your personal health.
                </p>
            </div>
        </div>
    );
};

export default Glossary;
