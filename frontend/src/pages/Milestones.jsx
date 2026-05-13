import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Award, Flame, TrendingUp, Heart, Pill, Target, Users, Info } from "lucide-react";

const StatCard = ({ icon: Icon, eyebrow, value, sub, testId }) => (
    <div className="tactile-card p-5 sm:p-6" data-testid={testId}>
        <Icon className="w-4 h-4 text-primary mb-2" strokeWidth={1.5} />
        <div className="label-eyebrow">{eyebrow}</div>
        <div className="font-display text-3xl font-medium tracking-tight mt-2">{value ?? "—"}</div>
        {sub && <div className="text-xs text-muted-foreground mt-2">{sub}</div>}
    </div>
);

const Milestones = () => {
    const [m, setM] = useState(null);
    const [c, setC] = useState(null);

    useEffect(() => {
        Promise.all([api.get("/milestones"), api.get("/community/averages")])
            .then(([rm, rc]) => {
                setM(rm.data);
                setC(rc.data);
            });
    }, []);

    if (!m) return <div className="text-muted-foreground" data-testid="milestones-loading">Loading…</div>;

    const personalCompliance = m.diet_days_logged > 0
        ? Math.round((m.days_meeting_protein / m.diet_days_logged) * 100)
        : null;

    const communityReady = c && c.users_count >= (c.min_users_threshold || 5);

    return (
        <div className="max-w-5xl mx-auto fade-up" data-testid="milestones-root">
            <div className="label-eyebrow">Milestones</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Your records.</h1>
            <p className="text-muted-foreground mt-3 max-w-2xl">
                Recovery isn't a race against anyone else. These are <em>your</em> personal bests — quiet evidence that things are moving.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
                <StatCard
                    icon={Flame}
                    eyebrow="Current streak"
                    value={m.current_streak_days}
                    sub="days sober"
                    testId="ms-streak"
                />
                <StatCard
                    icon={TrendingUp}
                    eyebrow="Best protein day"
                    value={m.best_protein_day ? `${m.best_protein_day.protein_g}g` : null}
                    sub={m.best_protein_day ? new Date(m.best_protein_day.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }) : "Log some meals to start"}
                    testId="ms-best-protein"
                />
                <StatCard
                    icon={Award}
                    eyebrow="Best protein streak"
                    value={m.best_protein_streak || 0}
                    sub="consecutive days ≥140g"
                    testId="ms-protein-streak"
                />
                <StatCard
                    icon={Heart}
                    eyebrow="Best day"
                    value={m.best_rating_day ? `${m.best_rating_day.rating}/10` : null}
                    sub={m.best_rating_day ? new Date(m.best_rating_day.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }) : "—"}
                    testId="ms-best-rating"
                />
                <StatCard
                    icon={Heart}
                    eyebrow="Best 7-day mood"
                    value={m.best_7d_mood_avg ? `${m.best_7d_mood_avg}/10` : null}
                    sub={m.best_7d_window_end ? `ending ${new Date(m.best_7d_window_end).toLocaleDateString(undefined, { month: "short", day: "numeric" })}` : "Need 4+ entries in 7 days"}
                    testId="ms-best-week"
                />
                <StatCard
                    icon={Pill}
                    eyebrow="Med adherence · 30d"
                    value={m.med_adherence_30d_pct !== null ? `${m.med_adherence_30d_pct}%` : null}
                    sub={m.med_adherence_30d_pct !== null ? "" : "Add a medication to track"}
                    testId="ms-med-adherence"
                />
                <StatCard
                    icon={Target}
                    eyebrow="Goals completed"
                    value={m.goals_completed}
                    sub="lifetime"
                    testId="ms-goals-completed"
                />
                <StatCard
                    icon={TrendingUp}
                    eyebrow="Protein target hit"
                    value={personalCompliance !== null ? `${personalCompliance}%` : null}
                    sub={`${m.days_meeting_protein} of ${m.diet_days_logged} day(s)`}
                    testId="ms-protein-compliance"
                />
                <StatCard
                    icon={Heart}
                    eyebrow="Diary entries"
                    value={m.diary_entries}
                    sub={m.avg_rating_all_time !== null ? `avg ${m.avg_rating_all_time}/10` : ""}
                    testId="ms-diary-count"
                />
            </div>

            {/* Community context */}
            <div className="mt-12">
                <div className="flex items-center gap-2 mb-1">
                    <Users className="w-4 h-4 text-primary" strokeWidth={1.5} />
                    <div className="label-eyebrow !text-foreground">Anonymous community context · last 30 days</div>
                </div>
                <p className="text-xs text-muted-foreground mb-5 max-w-2xl">
                    For context, not comparison. No names, no ranking. Aggregated across all Anchor users — only shown when there are at least {c?.min_users_threshold || 5} people in the data.
                </p>
                {!communityReady ? (
                    <div className="tactile-card p-6 text-sm text-muted-foreground flex items-start gap-2" data-testid="community-not-ready">
                        <Info className="w-4 h-4 mt-0.5 shrink-0" strokeWidth={1.5} />
                        <span>Not enough community data yet ({c?.users_count || 0} of {c?.min_users_threshold || 5} users needed). Community averages will appear here once enough people are logging.</span>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="tactile-card p-5" data-testid="community-mood">
                            <div className="label-eyebrow">Avg mood</div>
                            <div className="font-display text-2xl font-medium tracking-tight mt-2">{c.avg_mood ?? "—"}<span className="text-sm text-muted-foreground">/10</span></div>
                        </div>
                        <div className="tactile-card p-5" data-testid="community-protein">
                            <div className="label-eyebrow">Avg protein</div>
                            <div className="font-display text-2xl font-medium tracking-tight mt-2">{c.avg_protein_g}<span className="text-sm text-muted-foreground">g</span></div>
                        </div>
                        <div className="tactile-card p-5" data-testid="community-salt">
                            <div className="label-eyebrow">Avg salt</div>
                            <div className="font-display text-2xl font-medium tracking-tight mt-2">{c.avg_salt_g}<span className="text-sm text-muted-foreground">g</span></div>
                        </div>
                        <div className="tactile-card p-5" data-testid="community-water">
                            <div className="label-eyebrow">Avg water</div>
                            <div className="font-display text-2xl font-medium tracking-tight mt-2">{c.avg_water_ml}<span className="text-sm text-muted-foreground">ml</span></div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Milestones;
