import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Phone, ExternalLink, MessageSquareText, Heart } from "lucide-react";

const HotlineCard = ({ h }) => {
    const isText = (h.categories || []).includes("text");
    const Icon = isText ? MessageSquareText : Phone;
    return (
        <div className="tactile-card p-5 sm:p-6" data-testid={`hotline-${h.name.replace(/\s+/g, "-").toLowerCase()}`}>
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                    <div className="font-display text-lg font-medium tracking-tight">{h.name}</div>
                    {h.phone && (
                        <a href={isText ? "#" : `tel:${h.phone.replace(/[^0-9+]/g, "")}`} className="inline-flex items-center gap-2 mt-2 text-primary font-medium hover:underline">
                            <Icon className="w-4 h-4" strokeWidth={1.5} /> {h.phone}
                        </a>
                    )}
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{h.description}</p>
                </div>
            </div>
            <a href={h.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-primary mt-3">
                {h.url.replace(/^https?:\/\//, "").replace(/\/$/, "")} <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
            </a>
        </div>
    );
};

const Crisis = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/crisis").then((r) => setData(r.data)).finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="text-muted-foreground" data-testid="crisis-loading">Loading…</div>;
    if (!data) return null;

    const isSingle = data.region && data.regions.length === 1;
    const lists = isSingle ? { [data.region]: data.hotlines } : data.hotlines;

    return (
        <div className="max-w-4xl mx-auto fade-up" data-testid="crisis-root">
            <div className="label-eyebrow">Help</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">You're not alone.</h1>
            <p className="text-muted-foreground mt-3 max-w-2xl">
                If you're in crisis, having strong urges, or just need to talk — please reach out. These services are free, confidential, and available now.
            </p>

            <div className="tactile-card p-5 mt-8 bg-[hsl(13_54%_96%)] border-[hsl(13_54%_85%)]" data-testid="emergency-card">
                <div className="flex items-start gap-3">
                    <Heart className="w-5 h-5 text-accent mt-0.5" strokeWidth={1.5} />
                    <div>
                        <div className="font-medium">In immediate danger?</div>
                        <p className="text-sm text-muted-foreground mt-1">
                            If you or someone else is in immediate physical danger, call <span className="font-medium text-foreground">911 (US)</span> or <span className="font-medium text-foreground">999 (UK)</span> right now.
                        </p>
                    </div>
                </div>
            </div>

            {!data.region && (
                <p className="text-xs text-muted-foreground mt-8 mb-2">
                    Showing both US and UK resources. Set your region in <a href="/app/profile" className="text-primary hover:underline">Profile</a> to filter.
                </p>
            )}

            {Object.entries(lists).map(([region, list]) => (
                <section key={region} className="mt-8" data-testid={`crisis-region-${region}`}>
                    <div className="label-eyebrow mb-3">{region === "US" ? "United States" : "United Kingdom"}</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {list.map((h) => <HotlineCard key={h.name} h={h} />)}
                    </div>
                </section>
            ))}
        </div>
    );
};

export default Crisis;
