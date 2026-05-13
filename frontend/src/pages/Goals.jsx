import React, { useEffect, useState } from "react";
import { api, mondayOf } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Checkbox } from "../components/ui/checkbox";
import { Trash2, Plus } from "lucide-react";
import { toast } from "sonner";

const Goals = () => {
    const [weekStart, setWeekStart] = useState(mondayOf());
    const [goals, setGoals] = useState([]);
    const [title, setTitle] = useState("");

    const load = async () => {
        const { data } = await api.get("/goals", { params: { week_start: weekStart } });
        setGoals(data);
    };

    useEffect(() => {
        load();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [weekStart]);

    const add = async (e) => {
        e.preventDefault();
        if (!title.trim()) return;
        try {
            await api.post("/goals", { title: title.trim(), week_start: weekStart, completed: false });
            setTitle("");
            await load();
        } catch (err) {
            toast.error("Could not add");
        }
    };

    const toggle = async (g) => {
        await api.patch(`/goals/${g.id}`, { completed: !g.completed });
        await load();
    };

    const remove = async (id) => {
        await api.delete(`/goals/${id}`);
        await load();
    };

    const shiftWeek = (delta) => {
        const d = new Date(weekStart);
        d.setDate(d.getDate() + delta * 7);
        setWeekStart(d.toISOString().slice(0, 10));
    };

    const done = goals.filter((g) => g.completed).length;

    return (
        <div className="max-w-3xl mx-auto fade-up" data-testid="goals-root">
            <div className="label-eyebrow">Weekly goals</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Small commitments.</h1>
            <p className="text-muted-foreground mt-3">Pick 3–5. Specific beats ambitious.</p>

            <div className="flex items-center justify-between mt-8">
                <button onClick={() => shiftWeek(-1)} data-testid="goals-prev-week" className="text-sm text-muted-foreground hover:text-foreground">← Previous week</button>
                <div className="text-sm font-medium">Week of {new Date(weekStart).toLocaleDateString(undefined, { month: "long", day: "numeric" })}</div>
                <button onClick={() => shiftWeek(1)} data-testid="goals-next-week" className="text-sm text-muted-foreground hover:text-foreground">Next week →</button>
            </div>

            <form onSubmit={add} className="flex gap-2 mt-6">
                <Input data-testid="goals-input" placeholder="e.g. Walk 30 minutes, 4 days" value={title} onChange={(e) => setTitle(e.target.value)} />
                <Button type="submit" data-testid="goals-add-btn" className="rounded-full px-6">
                    <Plus className="w-4 h-4 mr-1" strokeWidth={1.5} /> Add
                </Button>
            </form>

            <div className="mt-8">
                <div className="label-eyebrow mb-3">Progress · {done} of {goals.length}</div>
                <div className="space-y-2">
                    {goals.length === 0 && <div className="text-sm text-muted-foreground tactile-card p-6">No goals for this week yet.</div>}
                    {goals.map((g) => (
                        <label key={g.id} className="tactile-card p-4 flex items-center gap-4 cursor-pointer group" data-testid={`goal-row-${g.id}`}>
                            <Checkbox
                                checked={g.completed}
                                onCheckedChange={() => toggle(g)}
                                data-testid={`goal-check-${g.id}`}
                                className="w-6 h-6 rounded-full"
                            />
                            <div className={`flex-1 transition-colors ${g.completed ? "line-through text-muted-foreground" : ""}`}>{g.title}</div>
                            <button
                                type="button"
                                onClick={(e) => { e.preventDefault(); remove(g.id); }}
                                className="text-muted-foreground opacity-0 group-hover:opacity-100 hover:text-destructive transition-all"
                                data-testid={`goal-delete-${g.id}`}
                            >
                                <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                            </button>
                        </label>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Goals;
