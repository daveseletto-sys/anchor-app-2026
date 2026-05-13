import React, { useEffect, useState } from "react";
import { api, todayStr } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Progress } from "../components/ui/progress";
import { toast } from "sonner";
import { Trash2, Droplet, Plus } from "lucide-react";

const TARGETS = { protein_g_min: 140, salt_g_max: 2, water_ml_max: 1500 };

const DietTracker = () => {
    const [meals, setMeals] = useState([]);
    const [totals, setTotals] = useState({ protein_g: 0, salt_g: 0, water_ml: 0, calories: 0 });
    const [form, setForm] = useState({ name: "", protein_g: "", salt_g: "", water_ml: "", calories: "" });
    const [submitting, setSubmitting] = useState(false);

    const load = async () => {
        const d = todayStr();
        const [m, t] = await Promise.all([api.get("/meals", { params: { date_str: d } }), api.get("/meals/totals", { params: { date_str: d } })]);
        setMeals(m.data);
        setTotals(t.data.totals);
    };

    useEffect(() => {
        load();
    }, []);

    const setField = (k, v) => setForm((p) => ({ ...p, [k]: v }));

    const addMeal = async (e) => {
        e.preventDefault();
        if (!form.name) return;
        setSubmitting(true);
        try {
            await api.post("/meals", {
                date: todayStr(),
                name: form.name,
                protein_g: parseFloat(form.protein_g) || 0,
                salt_g: parseFloat(form.salt_g) || 0,
                water_ml: parseFloat(form.water_ml) || 0,
                calories: parseFloat(form.calories) || 0,
                notes: "",
            });
            setForm({ name: "", protein_g: "", salt_g: "", water_ml: "", calories: "" });
            await load();
            toast.success("Added");
        } catch (err) {
            toast.error("Could not save");
        } finally {
            setSubmitting(false);
        }
    };

    const quickWater = async (ml) => {
        await api.post("/water", { date: todayStr(), amount_ml: ml });
        await load();
    };

    const remove = async (id) => {
        await api.delete(`/meals/${id}`);
        await load();
    };

    const pct = (v, t) => Math.min(100, (v / Math.max(t, 0.0001)) * 100);

    return (
        <div className="max-w-5xl mx-auto fade-up" data-testid="diet-root">
            <div className="label-eyebrow">Diet tracker</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">What did you eat today?</h1>

            {/* Progress bars */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
                <div className="tactile-card p-6" data-testid="bar-protein">
                    <div className="flex items-baseline justify-between">
                        <div className="label-eyebrow">Protein</div>
                        <div className="text-xs text-muted-foreground">min 140g</div>
                    </div>
                    <div className="font-display text-3xl font-medium tracking-tight mt-2">
                        {totals.protein_g.toFixed(0)}<span className="text-base text-muted-foreground">g</span>
                    </div>
                    <Progress value={pct(totals.protein_g, TARGETS.protein_g_min)} className="mt-4 h-2" />
                </div>
                <div className="tactile-card p-6" data-testid="bar-salt">
                    <div className="flex items-baseline justify-between">
                        <div className="label-eyebrow">Salt</div>
                        <div className="text-xs text-muted-foreground">max 2g</div>
                    </div>
                    <div className={`font-display text-3xl font-medium tracking-tight mt-2 ${totals.salt_g > TARGETS.salt_g_max ? "text-accent" : ""}`}>
                        {totals.salt_g.toFixed(1)}<span className="text-base text-muted-foreground">g</span>
                    </div>
                    <Progress value={pct(totals.salt_g, TARGETS.salt_g_max)} className="mt-4 h-2" />
                </div>
                <div className="tactile-card p-6" data-testid="bar-water">
                    <div className="flex items-baseline justify-between">
                        <div className="label-eyebrow">Water</div>
                        <div className="text-xs text-muted-foreground">max 1.5L</div>
                    </div>
                    <div className={`font-display text-3xl font-medium tracking-tight mt-2 ${totals.water_ml > TARGETS.water_ml_max ? "text-accent" : ""}`}>
                        {totals.water_ml.toFixed(0)}<span className="text-base text-muted-foreground">ml</span>
                    </div>
                    <Progress value={pct(totals.water_ml, TARGETS.water_ml_max)} className="mt-4 h-2" />
                    <div className="flex gap-2 mt-4">
                        {[100, 250, 500].map((ml) => (
                            <button
                                key={ml}
                                onClick={() => quickWater(ml)}
                                data-testid={`water-quick-${ml}`}
                                className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-full bg-secondary hover:bg-primary/10 transition-colors"
                            >
                                <Droplet className="w-3 h-3" strokeWidth={1.5} /> +{ml}ml
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Add form */}
            <form onSubmit={addMeal} className="tactile-card p-6 sm:p-8 mt-8" data-testid="meal-form">
                <div className="label-eyebrow mb-4">Log a meal or item</div>
                <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
                    <Input data-testid="meal-name-input" placeholder="e.g. Grilled chicken & rice" value={form.name} onChange={(e) => setField("name", e.target.value)} className="md:col-span-2" />
                    <Input data-testid="meal-protein-input" type="number" placeholder="Protein (g)" value={form.protein_g} onChange={(e) => setField("protein_g", e.target.value)} />
                    <Input data-testid="meal-salt-input" type="number" step="0.1" placeholder="Salt (g)" value={form.salt_g} onChange={(e) => setField("salt_g", e.target.value)} />
                    <Input data-testid="meal-water-input" type="number" placeholder="Water (ml)" value={form.water_ml} onChange={(e) => setField("water_ml", e.target.value)} />
                    <Input data-testid="meal-calories-input" type="number" placeholder="Calories" value={form.calories} onChange={(e) => setField("calories", e.target.value)} />
                </div>
                <Button type="submit" disabled={submitting} data-testid="meal-submit-btn" className="rounded-full px-6 mt-5">
                    <Plus className="w-4 h-4 mr-1" strokeWidth={1.5} /> Add
                </Button>
            </form>

            {/* Meals list */}
            <h2 className="font-display text-2xl font-medium tracking-tight mt-12 mb-4">Today's log</h2>
            <div className="space-y-2">
                {meals.length === 0 && <div className="text-sm text-muted-foreground">Nothing logged yet.</div>}
                {meals.map((m) => (
                    <div key={m.id} className="tactile-card p-4 flex items-center justify-between" data-testid={`meal-row-${m.id}`}>
                        <div>
                            <div className="font-medium">{m.name}</div>
                            <div className="text-xs text-muted-foreground mt-0.5">
                                {m.protein_g > 0 && <span>{m.protein_g}g protein</span>}
                                {m.salt_g > 0 && <span> · {m.salt_g}g salt</span>}
                                {m.water_ml > 0 && <span> · {m.water_ml}ml water</span>}
                                {m.calories > 0 && <span> · {m.calories} cal</span>}
                            </div>
                        </div>
                        <button onClick={() => remove(m.id)} data-testid={`meal-delete-${m.id}`} className="text-muted-foreground hover:text-destructive">
                            <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DietTracker;
