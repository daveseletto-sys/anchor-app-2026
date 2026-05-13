import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Anchor, Sparkles, AlertCircle } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Stat = ({ label, value, unit }) => (
    <div>
        <div className="label-eyebrow">{label}</div>
        <div className="font-display text-3xl font-medium tracking-tight mt-1">
            {value}
            {unit && <span className="text-base text-muted-foreground ml-1">{unit}</span>}
        </div>
    </div>
);

const SharedView = () => {
    const { token } = useParams();
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get(`${API}/shared/${token}`)
            .then((r) => setData(r.data))
            .catch((e) => {
                const status = e?.response?.status;
                if (status === 404) setError("This link doesn't exist.");
                else if (status === 410) setError(e?.response?.data?.detail || "This link is no longer valid.");
                else setError("Could not load this link.");
            })
            .finally(() => setLoading(false));
    }, [token]);

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center text-muted-foreground" data-testid="shared-loading">Loading…</div>;
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8" data-testid="shared-error">
                <div className="tactile-card p-8 max-w-md text-center">
                    <AlertCircle className="w-8 h-8 mx-auto text-accent mb-4" strokeWidth={1.5} />
                    <h1 className="font-display text-2xl font-medium tracking-tight">Link unavailable</h1>
                    <p className="text-muted-foreground text-sm mt-3">{error}</p>
                </div>
            </div>
        );
    }

    const ds = data.diet_summary;
    const t = ds.targets;

    return (
        <div className="min-h-screen p-6 sm:p-12 fade-up" data-testid="shared-root">
            <div className="max-w-3xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-2 mb-2">
                    <Anchor className="w-5 h-5 text-primary" strokeWidth={1.5} />
                    <span className="font-display font-semibold tracking-tight">Anchor</span>
                </div>
                <div className="label-eyebrow">Shared by {data.owner_name}</div>
                <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">
                    {data.owner_name}'s check-in
                </h1>
                <div className="text-xs text-muted-foreground mt-2">
                    Read-only. Link expires {new Date(data.expires_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}
                </div>

                {/* Sobriety */}
                <div className="tactile-card p-6 sm:p-8 mt-8" data-testid="shared-sobriety">
                    <div className="label-eyebrow">Days sober</div>
                    <div className="font-display font-light text-7xl sm:text-8xl leading-none tracking-tighter mt-2 text-primary">
                        {data.sobriety.days_sober}
                    </div>
                    <div className="text-sm text-muted-foreground mt-3">
                        since {new Date(data.sobriety.sobriety_start).toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })}
                    </div>
                </div>

                {/* Last 7 days summary */}
                <div className="tactile-card p-6 sm:p-8 mt-5">
                    <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-accent" strokeWidth={1.5} />
                        <div className="label-eyebrow !text-foreground">Last 7 days</div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6">
                        <Stat label="Mood avg" value={data.diary_avg_rating ?? "—"} unit={data.diary_avg_rating !== null ? "/10" : ""} />
                        <Stat label="Avg protein" value={ds.avg_protein_g} unit="g" />
                        <Stat label="Avg salt" value={ds.avg_salt_g} unit="g" />
                        <Stat label="Avg water" value={ds.avg_water_ml} unit="ml" />
                    </div>
                    <div className="text-xs text-muted-foreground mt-4">
                        Targets: protein ≥ {t.protein_g_min}g · salt ≤ {t.salt_g_max}g · water ≤ {t.water_ml_max}ml per day · {ds.days_logged} day(s) logged
                    </div>
                </div>

                {/* Goals */}
                <div className="tactile-card p-6 sm:p-8 mt-5" data-testid="shared-goals">
                    <div className="label-eyebrow mb-4">This week's goals</div>
                    {data.goals.length === 0 ? (
                        <div className="text-sm text-muted-foreground">No goals set this week.</div>
                    ) : (
                        <div className="space-y-2">
                            {data.goals.map((g, i) => (
                                <div key={i} className={`text-sm ${g.completed ? "text-muted-foreground line-through" : ""}`}>
                                    {g.completed ? "✓" : "·"} {g.title}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Diary entries (only on full scope) */}
                {data.diary_entries.length > 0 && (
                    <div className="tactile-card p-6 sm:p-8 mt-5" data-testid="shared-diary">
                        <div className="label-eyebrow mb-4">Recent check-ins</div>
                        <div className="space-y-4">
                            {data.diary_entries.map((e, i) => (
                                <div key={i} className="border-b border-border pb-3 last:border-0">
                                    <div className="flex items-baseline justify-between">
                                        <div className="text-sm font-medium">
                                            {new Date(e.date).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}
                                        </div>
                                        <div className="font-display text-lg font-medium tracking-tight">{e.rating}/10</div>
                                    </div>
                                    {e.mood_tags?.length > 0 && (
                                        <div className="flex flex-wrap gap-1.5 mt-2">
                                            {e.mood_tags.map((t) => (
                                                <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-primary/10 text-primary">{t}</span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="text-xs text-muted-foreground mt-10 text-center">
                    Anchor — a private recovery companion. This is a read-only snapshot.
                </div>
            </div>
        </div>
    );
};

export default SharedView;
