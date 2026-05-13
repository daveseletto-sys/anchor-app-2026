import React, { useEffect, useState } from "react";
import { api, todayStr } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Checkbox } from "../components/ui/checkbox";
import { Trash2, Plus, Pill } from "lucide-react";
import { toast } from "sonner";

const Medications = () => {
    const [meds, setMeds] = useState([]);
    const [logs, setLogs] = useState([]);
    const [form, setForm] = useState({ name: "", dose: "", schedule: "", notes: "" });

    const load = async () => {
        const [m, l] = await Promise.all([
            api.get("/medications"),
            api.get("/medications/log", { params: { date_str: todayStr() } }),
        ]);
        setMeds(m.data);
        setLogs(l.data);
    };

    useEffect(() => {
        load();
    }, []);

    const setField = (k, v) => setForm((p) => ({ ...p, [k]: v }));

    const addMed = async (e) => {
        e.preventDefault();
        if (!form.name.trim()) return;
        try {
            await api.post("/medications", { ...form, active: true });
            setForm({ name: "", dose: "", schedule: "", notes: "" });
            toast.success("Medication added");
            await load();
        } catch (err) {
            toast.error("Could not add");
        }
    };

    const remove = async (id) => {
        await api.delete(`/medications/${id}`);
        await load();
    };

    const toggleActive = async (m) => {
        await api.patch(`/medications/${m.id}`, { active: !m.active });
        await load();
    };

    const isTakenToday = (medId) => {
        const log = logs.find((l) => l.medication_id === medId);
        return log ? log.taken : false;
    };

    const toggleTaken = async (med) => {
        const taken = !isTakenToday(med.id);
        await api.post("/medications/log", { medication_id: med.id, date: todayStr(), taken });
        await load();
    };

    const activeMeds = meds.filter((m) => m.active);
    const inactiveMeds = meds.filter((m) => !m.active);
    const takenCount = activeMeds.filter((m) => isTakenToday(m.id)).length;

    return (
        <div className="max-w-3xl mx-auto fade-up" data-testid="meds-root">
            <div className="label-eyebrow">Medications</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Stay on top of it.</h1>
            <p className="text-muted-foreground mt-3">Naltrexone, thiamine, supplements — track what you take and tick them off daily.</p>

            {/* Today's check-offs */}
            <div className="tactile-card p-6 sm:p-8 mt-10" data-testid="today-meds-card">
                <div className="flex items-center justify-between">
                    <div className="label-eyebrow">Today · {new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}</div>
                    <div className="text-sm text-muted-foreground">{takenCount} of {activeMeds.length} taken</div>
                </div>
                {activeMeds.length === 0 && <div className="mt-5 text-sm text-muted-foreground">No medications yet. Add one below.</div>}
                <div className="mt-5 space-y-2">
                    {activeMeds.map((m) => {
                        const taken = isTakenToday(m.id);
                        return (
                            <label key={m.id} className="flex items-center gap-4 p-3 rounded-2xl hover:bg-secondary cursor-pointer transition-colors" data-testid={`today-med-${m.id}`}>
                                <Checkbox
                                    checked={taken}
                                    onCheckedChange={() => toggleTaken(m)}
                                    className="w-6 h-6 rounded-full"
                                    data-testid={`today-med-check-${m.id}`}
                                />
                                <div className="flex-1">
                                    <div className={`font-medium ${taken ? "text-muted-foreground line-through" : ""}`}>{m.name}</div>
                                    <div className="text-xs text-muted-foreground">{[m.dose, m.schedule].filter(Boolean).join(" · ")}</div>
                                </div>
                            </label>
                        );
                    })}
                </div>
            </div>

            {/* Add new */}
            <form onSubmit={addMed} className="tactile-card p-6 sm:p-8 mt-6" data-testid="med-form">
                <div className="label-eyebrow mb-4">Add a medication</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Input data-testid="med-name-input" placeholder="Name (e.g. Naltrexone)" value={form.name} onChange={(e) => setField("name", e.target.value)} />
                    <Input data-testid="med-dose-input" placeholder="Dose (e.g. 50mg)" value={form.dose} onChange={(e) => setField("dose", e.target.value)} />
                    <Input data-testid="med-schedule-input" placeholder="Schedule (e.g. Daily, morning)" value={form.schedule} onChange={(e) => setField("schedule", e.target.value)} />
                    <Input data-testid="med-notes-input" placeholder="Notes (optional)" value={form.notes} onChange={(e) => setField("notes", e.target.value)} />
                </div>
                <Button type="submit" data-testid="med-add-btn" className="rounded-full px-6 mt-5">
                    <Plus className="w-4 h-4 mr-1" strokeWidth={1.5} /> Add medication
                </Button>
            </form>

            {/* All meds */}
            <h2 className="font-display text-2xl font-medium tracking-tight mt-12 mb-4">All medications</h2>
            <div className="space-y-2">
                {meds.length === 0 && <div className="text-sm text-muted-foreground">No medications.</div>}
                {[...activeMeds, ...inactiveMeds].map((m) => (
                    <div key={m.id} className={`tactile-card p-4 flex items-center justify-between ${m.active ? "" : "opacity-60"}`} data-testid={`med-row-${m.id}`}>
                        <div className="flex items-center gap-3">
                            <Pill className="w-4 h-4 text-primary" strokeWidth={1.5} />
                            <div>
                                <div className="font-medium">{m.name}</div>
                                <div className="text-xs text-muted-foreground">{[m.dose, m.schedule].filter(Boolean).join(" · ") || "—"}</div>
                                {m.notes && <div className="text-xs text-muted-foreground italic mt-1">{m.notes}</div>}
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <button onClick={() => toggleActive(m)} data-testid={`med-toggle-${m.id}`} className="text-xs text-muted-foreground hover:text-foreground">
                                {m.active ? "Pause" : "Resume"}
                            </button>
                            <button onClick={() => remove(m.id)} className="text-muted-foreground hover:text-destructive" data-testid={`med-delete-${m.id}`}>
                                <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Medications;
