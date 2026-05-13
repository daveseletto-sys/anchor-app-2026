import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Sparkles, RefreshCw, Loader2 } from "lucide-react";
import { toast } from "sonner";

const WeeklyInsight = () => {
    const [text, setText] = useState(null);
    const [createdAt, setCreatedAt] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    const fetchCached = async () => {
        try {
            const { data } = await api.get("/insights/weekly");
            setText(data.text);
            setCreatedAt(data.created_at);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCached();
    }, []);

    const generate = async () => {
        setGenerating(true);
        try {
            const { data } = await api.post("/insights/weekly");
            setText(data.text);
            setCreatedAt(new Date().toISOString());
            toast.success("Reflection ready");
        } catch (err) {
            toast.error(err?.response?.data?.detail || "Could not generate");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="tactile-card p-6 sm:p-8" data-testid="weekly-insight-card">
            <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-accent" strokeWidth={1.5} />
                    <div className="label-eyebrow !text-foreground">This week's reflection</div>
                </div>
                <button
                    onClick={generate}
                    disabled={generating}
                    data-testid="weekly-insight-refresh"
                    className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline disabled:opacity-50"
                >
                    {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" strokeWidth={1.5} /> : <RefreshCw className="w-3.5 h-3.5" strokeWidth={1.5} />}
                    {text ? "Regenerate" : "Generate"}
                </button>
            </div>

            {loading && <div className="mt-4 text-sm text-muted-foreground">Loading…</div>}

            {!loading && !text && !generating && (
                <p className="mt-4 text-sm text-muted-foreground">
                    A gentle, private reflection on your week — drawn from your diary, diet, and meds. Tap <span className="text-primary">Generate</span> to read this week's.
                </p>
            )}

            {generating && !text && (
                <div className="mt-4 text-sm text-muted-foreground flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} /> Reflecting on your week…
                </div>
            )}

            {text && (
                <div className="mt-5">
                    <p className="font-body text-base leading-[1.75] whitespace-pre-wrap text-foreground/90" data-testid="weekly-insight-text">{text}</p>
                    {createdAt && (
                        <div className="text-xs text-muted-foreground mt-4">
                            Updated {new Date(createdAt).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default WeeklyInsight;
