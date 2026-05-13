import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Sparkles, RefreshCw, Loader2, Mail } from "lucide-react";
import { toast } from "sonner";

const WeeklyInsight = () => {
    const [text, setText] = useState(null);
    const [createdAt, setCreatedAt] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [emailing, setEmailing] = useState(false);

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

    const emailMe = async () => {
        setEmailing(true);
        try {
            await api.post("/insights/email-digest");
            toast.success("Digest emailed to you");
        } catch (err) {
            toast.error(err?.response?.data?.detail || "Could not email digest");
        } finally {
            setEmailing(false);
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
                    <div className="flex items-center justify-between mt-4 flex-wrap gap-3">
                        {createdAt && (
                            <div className="text-xs text-muted-foreground">
                                Updated {new Date(createdAt).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}
                            </div>
                        )}
                        <button
                            onClick={emailMe}
                            disabled={emailing}
                            data-testid="weekly-insight-email"
                            className="inline-flex items-center gap-1.5 text-xs text-primary border border-primary/30 rounded-full px-3 py-1.5 hover:bg-primary/5 disabled:opacity-50"
                        >
                            {emailing ? <Loader2 className="w-3.5 h-3.5 animate-spin" strokeWidth={1.5} /> : <Mail className="w-3.5 h-3.5" strokeWidth={1.5} />}
                            {emailing ? "Sending…" : "Email me this"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WeeklyInsight;
