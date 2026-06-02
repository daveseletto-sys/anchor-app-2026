import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Anchor, ExternalLink, ShieldCheck } from "lucide-react";
import { api } from "../lib/api";

const Sources = () => {
    const [data, setData] = useState(null);

    useEffect(() => {
        api.get("/sources").then((r) => setData(r.data)).catch(() => setData({ sources: [], disclaimer: "" }));
    }, []);

    return (
        <div className="min-h-screen bg-background p-6 sm:p-12 fade-up" data-testid="sources-root">
            <div className="max-w-3xl mx-auto">
                <Link to="/" className="flex items-center gap-2 mb-8">
                    <Anchor className="w-5 h-5 text-primary" strokeWidth={1.5} />
                    <span className="font-display font-semibold tracking-tight">Anchor</span>
                </Link>

                <div className="label-eyebrow">Medical references</div>
                <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Where our information comes from.</h1>
                <p className="text-muted-foreground mt-3 max-w-2xl">
                    Anchor draws on public health and clinical sources. Below are the organisations whose published guidance informs the definitions, reference ranges, and dietary information in this app.
                </p>

                <div className="tactile-card p-5 mt-8 bg-[hsl(136_18%_94%)] border-[hsl(136_18%_82%)] flex items-start gap-3" data-testid="medical-disclaimer">
                    <ShieldCheck className="w-5 h-5 text-primary mt-0.5 shrink-0" strokeWidth={1.5} />
                    <p className="text-sm text-foreground/85 leading-relaxed">
                        {data?.disclaimer || "Anchor is a self-tracking tool. It does not provide medical advice. Always consult a qualified clinician about your personal health."}
                    </p>
                </div>

                <h2 className="font-display text-2xl font-medium tracking-tight mt-12 mb-4">Primary sources</h2>
                <div className="space-y-4">
                    {(data?.sources || []).map((s) => (
                        <div key={s.name} className="tactile-card p-5" data-testid={`source-${s.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 30)}`}>
                            <div className="flex items-start justify-between gap-3 flex-wrap">
                                <div className="font-display font-medium tracking-tight">{s.name}</div>
                                <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline inline-flex items-center gap-1">
                                    {s.url.replace(/^https?:\/\//, "").replace(/\/$/, "")} <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                                </a>
                            </div>
                            <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{s.purpose}</p>
                        </div>
                    ))}
                </div>

                <h2 className="font-display text-2xl font-medium tracking-tight mt-12 mb-3">In-app citations</h2>
                <p className="text-sm text-muted-foreground mb-4">Every term in the in-app <Link to="/app/glossary" className="text-primary underline">Glossary</Link> links to the public information source it came from — tap any term to see the publishing organisation and a link to the original page. Anchor does not interpret medical information or provide medical advice.</p>

                <div className="text-xs text-muted-foreground mt-12 pt-6 border-t border-border flex flex-wrap gap-6">
                    <Link to="/" className="hover:text-primary">Home</Link>
                    <Link to="/privacy" className="hover:text-primary">Privacy</Link>
                    <Link to="/support" className="hover:text-primary">Support</Link>
                </div>
            </div>
        </div>
    );
};

export default Sources;
