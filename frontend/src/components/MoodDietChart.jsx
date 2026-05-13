import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { Activity, TrendingUp, TrendingDown, Minus } from "lucide-react";

const CorrelationPill = ({ label, value }) => {
    if (value === null || value === undefined) {
        return (
            <div className="flex items-center gap-2 text-xs">
                <Minus className="w-3 h-3 text-muted-foreground" strokeWidth={1.5} />
                <span className="text-muted-foreground">{label}: not enough data</span>
            </div>
        );
    }
    const strong = Math.abs(value) >= 0.3;
    const pos = value > 0;
    const Icon = pos ? TrendingUp : TrendingDown;
    const cls = strong ? (pos ? "text-primary" : "text-accent") : "text-muted-foreground";
    return (
        <div className={`flex items-center gap-2 text-xs ${cls}`}>
            <Icon className="w-3 h-3" strokeWidth={1.5} />
            <span className="font-medium">{label}</span>
            <span className="text-muted-foreground">{value > 0 ? "+" : ""}{value}</span>
        </div>
    );
};

const MoodDietChart = () => {
    const [data, setData] = useState(null);

    useEffect(() => {
        api.get("/correlations", { params: { days: 30 } }).then((r) => setData(r.data));
    }, []);

    if (!data) return null;

    // Hide if essentially no data
    const hasData = data.series.some((s) => s.rating !== null) || data.series.some((s) => s.protein_g > 0);
    if (!hasData) {
        return (
            <div className="tactile-card p-6 sm:p-8" data-testid="mood-diet-chart-empty">
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-primary" strokeWidth={1.5} />
                    <div className="label-eyebrow !text-foreground">Mood &amp; diet patterns</div>
                </div>
                <p className="mt-4 text-sm text-muted-foreground">
                    Once you've logged a few days of meals and check-ins, you'll see a chart here that reveals how your nutrition relates to how you feel.
                </p>
            </div>
        );
    }

    return (
        <div className="tactile-card p-6 sm:p-8" data-testid="mood-diet-chart">
            <div className="flex items-start justify-between gap-4 flex-wrap">
                <div>
                    <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary" strokeWidth={1.5} />
                        <div className="label-eyebrow !text-foreground">Mood &amp; diet · last 30 days</div>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">How your nutrition relates to how you feel.</div>
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 items-center" data-testid="correlations-pills">
                    <CorrelationPill label="Protein ↔ Mood" value={data.correlations.protein} />
                    <CorrelationPill label="Salt ↔ Mood" value={data.correlations.salt} />
                    <CorrelationPill label="Water ↔ Mood" value={data.correlations.water} />
                </div>
            </div>

            <div className="h-64 mt-6">
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={data.series} margin={{ top: 10, right: 10, bottom: 0, left: -8 }}>
                        <CartesianGrid stroke="hsl(42 20% 90%)" strokeDasharray="2 4" />
                        <XAxis
                            dataKey="date"
                            tick={{ fontSize: 10, fill: "hsl(127 4% 36%)" }}
                            tickFormatter={(d) => d ? d.slice(5) : ""}
                            interval="preserveStartEnd"
                            minTickGap={20}
                        />
                        <YAxis yAxisId="left" domain={[0, 10]} tick={{ fontSize: 10, fill: "hsl(127 4% 36%)" }} label={{ value: "mood", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: "hsl(127 4% 36%)" } }} />
                        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: "hsl(127 4% 36%)" }} label={{ value: "protein g", angle: 90, position: "insideRight", style: { fontSize: 10, fill: "hsl(127 4% 36%)" } }} />
                        <Tooltip
                            contentStyle={{ background: "hsl(127 9% 19%)", border: "none", borderRadius: 12, color: "#fff", fontSize: 12 }}
                            labelStyle={{ color: "#fff", marginBottom: 4 }}
                        />
                        <Legend wrapperStyle={{ fontSize: 11 }} />
                        <Bar yAxisId="right" dataKey="protein_g" fill="hsl(136 18% 55%)" fillOpacity={0.7} name="Protein (g)" radius={[4, 4, 0, 0]} />
                        <Line yAxisId="left" type="monotone" dataKey="rating" stroke="hsl(13 54% 55%)" strokeWidth={2.5} dot={{ r: 3, fill: "hsl(13 54% 55%)" }} connectNulls name="Mood (1–10)" />
                    </ComposedChart>
                </ResponsiveContainer>
            </div>

            <div className="text-xs text-muted-foreground mt-3">
                Numbers near +1 mean strong positive link, near −1 strong negative, near 0 no clear link. Based on {data.correlations.n} day{data.correlations.n === 1 ? "" : "s"} with both a mood entry and meal log.
            </div>
        </div>
    );
};

export default MoodDietChart;
