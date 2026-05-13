import React, { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import { Input } from "../components/ui/input";
import { Search } from "lucide-react";

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
                                </div>
                            ))}
                        </div>
                    </section>
                ))}
                {grouped.length === 0 && <div className="text-sm text-muted-foreground">No matches.</div>}
            </div>
        </div>
    );
};

export default Glossary;
