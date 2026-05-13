import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import ProgressRing from "../components/ProgressRing";
import WeeklyInsight from "../components/WeeklyInsight";
import { Link } from "react-router-dom";
import { ArrowRight, Sparkles } from "lucide-react";

const Dashboard = () => {
    const { user } = useAuth();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/dashboard")
            .then((r) => setData(r.data))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return <div className="text-muted-foreground" data-testid="dashboard-loading">Loading…</div>;
    }
    if (!data) return null;

    const greeting = (() => {
        const h = new Date().getHours();
        if (h < 12) return "Good morning";
        if (h < 18) return "Good afternoon";
        return "Good evening";
    })();

    const protein = data.today.totals.protein_g || 0;
    const salt = data.today.totals.salt_g || 0;
    const water = data.today.totals.water_ml || 0;
    const targets = data.today.targets;

    const goalsDone = (data.goals || []).filter((g) => g.completed).length;
    const goalsTotal = (data.goals || []).length;

    return (
        <div className="max-w-6xl mx-auto fade-up" data-testid="dashboard-root">
            <div className="flex items-end justify-between flex-wrap gap-4">
                <div>
                    <div className="label-eyebrow">{greeting}</div>
                    <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">
                        {user?.name || "Friend"}.
                    </h1>
                </div>
                <div className="text-sm text-muted-foreground">{new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}</div>
            </div>

            {/* Bento grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mt-10">
                {/* Sobriety streak - hero */}
                <div className="tactile-card p-8 md:col-span-2 md:row-span-2 flex flex-col justify-between min-h-[280px]" data-testid="card-sobriety">
                    <div>
                        <div className="label-eyebrow">Days sober</div>
                        <div className="font-display font-light text-[88px] sm:text-[112px] leading-none tracking-tighter mt-2 text-primary">
                            {data.sobriety.days_sober}
                        </div>
                        <div className="text-muted-foreground mt-2">
                            since {new Date(data.sobriety.sobriety_start).toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })}
                        </div>
                    </div>
                    <div className="mt-6 flex items-center gap-2 text-sm">
                        <Sparkles className="w-4 h-4 text-accent" strokeWidth={1.5} />
                        <span className="text-muted-foreground">
                            {data.sobriety.days_sober === 0
                                ? "Today is day one. That's enough."
                                : `Every day above zero counts. You're at ${data.sobriety.days_sober}.`}
                        </span>
                    </div>
                </div>

                {/* Protein */}
                <div className="tactile-card p-6 flex flex-col items-center justify-center" data-testid="card-protein">
                    <ProgressRing value={protein} target={targets.protein_g_min} label="Protein" unit="g" color="primary" variant="fill" testId="ring-protein" />
                </div>

                {/* Salt */}
                <div className="tactile-card p-6 flex flex-col items-center justify-center" data-testid="card-salt">
                    <ProgressRing value={salt} target={targets.salt_g_max} label="Salt" unit="g" color="terracotta" variant="limit" testId="ring-salt" />
                </div>

                {/* Water */}
                <div className="tactile-card p-6 flex flex-col items-center justify-center" data-testid="card-water">
                    <ProgressRing value={water} target={targets.water_ml_max} label="Water" unit="ml" color="sky" variant="limit" testId="ring-water" />
                </div>

                {/* Today's mood */}
                <div className="tactile-card p-6" data-testid="card-mood">
                    <div className="label-eyebrow">Today's rating</div>
                    {data.today.diary ? (
                        <div className="mt-3">
                            <div className="font-display text-5xl font-light tracking-tight">
                                {data.today.diary.rating}
                                <span className="text-base text-muted-foreground ml-1">/10</span>
                            </div>
                            <div className="flex flex-wrap gap-1.5 mt-3">
                                {(data.today.diary.mood_tags || []).map((t) => (
                                    <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-primary/10 text-primary">
                                        {t}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <Link to="/app/diary" className="mt-3 inline-flex items-center gap-2 text-primary font-medium text-sm">
                            Log today's check-in <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                        </Link>
                    )}
                </div>
            </div>

            {/* Second row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-5">
                <div className="tactile-card p-6" data-testid="card-weekly-avg">
                    <div className="label-eyebrow">Weekly avg mood</div>
                    <div className="font-display text-5xl font-light tracking-tight mt-2">
                        {data.weekly_rating_avg !== null ? data.weekly_rating_avg : "—"}
                        {data.weekly_rating_avg !== null && <span className="text-base text-muted-foreground ml-1">/10</span>}
                    </div>
                    <div className="text-xs text-muted-foreground mt-2">Last 7 days</div>
                </div>

                <div className="tactile-card p-6 md:col-span-2" data-testid="card-week-goals">
                    <div className="flex items-center justify-between">
                        <div className="label-eyebrow">This week's goals</div>
                        <Link to="/app/goals" className="text-xs text-primary hover:underline">Manage</Link>
                    </div>
                    <div className="font-display text-4xl font-light tracking-tight mt-2">
                        {goalsDone}<span className="text-muted-foreground"> / {goalsTotal}</span>
                    </div>
                    <div className="mt-4 space-y-2">
                        {(data.goals || []).slice(0, 4).map((g) => (
                            <div key={g.id} className={`text-sm ${g.completed ? "text-muted-foreground line-through" : ""}`}>
                                · {g.title}
                            </div>
                        ))}
                        {goalsTotal === 0 && (
                            <Link to="/app/goals" className="text-sm text-primary inline-flex items-center gap-1">
                                Set this week's goals <ArrowRight className="w-3.5 h-3.5" strokeWidth={1.5} />
                            </Link>
                        )}
                    </div>
                </div>
            </div>

            {/* Weekly insight */}
            <div className="mt-5">
                <WeeklyInsight />
            </div>
        </div>
    );
};

export default Dashboard;
