import React, { useEffect, useState } from "react";
import { api, imageFileToJpegBase64, todayStr } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import { Trash2, Upload, Loader2, Plus, X } from "lucide-react";
import { toast } from "sonner";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const DEFAULT_MARKERS = [
    { name: "ALT", value: "", unit: "U/L", reference_range: "7–56" },
    { name: "AST", value: "", unit: "U/L", reference_range: "10–40" },
    { name: "GGT", value: "", unit: "U/L", reference_range: "9–48" },
    { name: "Bilirubin (total)", value: "", unit: "mg/dL", reference_range: "0.1–1.2" },
    { name: "MCV", value: "", unit: "fL", reference_range: "80–100" },
];

const BloodTests = () => {
    const [tests, setTests] = useState([]);
    const [date, setDate] = useState(todayStr());
    const [lab, setLab] = useState("");
    const [notes, setNotes] = useState("");
    const [markers, setMarkers] = useState(DEFAULT_MARKERS);
    const [submitting, setSubmitting] = useState(false);
    const [extracting, setExtracting] = useState(false);

    const load = async () => {
        const { data } = await api.get("/blood-tests");
        setTests(data);
    };

    useEffect(() => {
        load();
    }, []);

    const setMarker = (i, key, val) => {
        setMarkers((prev) => prev.map((m, idx) => (idx === i ? { ...m, [key]: val } : m)));
    };

    const addMarker = () => setMarkers((p) => [...p, { name: "", value: "", unit: "", reference_range: "" }]);
    const removeMarker = (i) => setMarkers((p) => p.filter((_, idx) => idx !== i));

    const onExtract = async (file) => {
        if (!file) return;
        setExtracting(true);
        try {
            const b64 = await imageFileToJpegBase64(file);
            const { data } = await api.post("/blood-tests/extract", { image_base64: b64 });
            if (data.date) setDate(data.date.slice(0, 10));
            if (data.lab) setLab(data.lab);
            if (data.notes) setNotes(data.notes);
            const found = Array.isArray(data.markers) ? data.markers : [];
            if (found.length > 0) {
                setMarkers(found.map((m) => ({
                    name: m.name || "",
                    value: m.value ?? "",
                    unit: m.unit || "",
                    reference_range: m.reference_range || "",
                })));
                toast.success(`Extracted ${found.length} marker${found.length === 1 ? "" : "s"} — review and save`);
            } else {
                toast.message("We couldn't read markers from that photo", {
                    description: "Try a clearer, well-lit photo of the results table, or enter the markers manually below.",
                });
            }
        } catch (err) {
            toast.error(err?.response?.data?.detail || err?.message || "Extraction failed");
        } finally {
            setExtracting(false);
        }
    };

    const save = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            const clean = markers
                .filter((m) => m.name && m.value !== "" && m.value !== null)
                .map((m) => ({
                    name: m.name,
                    value: parseFloat(m.value) || 0,
                    unit: m.unit || "",
                    reference_range: m.reference_range || "",
                }));
            if (clean.length === 0) {
                toast.error("Add at least one marker");
                return;
            }
            await api.post("/blood-tests", { date, lab, markers: clean, notes });
            toast.success("Blood test saved");
            setMarkers(DEFAULT_MARKERS);
            setLab("");
            setNotes("");
            await load();
        } catch (err) {
            toast.error("Could not save");
        } finally {
            setSubmitting(false);
        }
    };

    const remove = async (id) => {
        await api.delete(`/blood-tests/${id}`);
        await load();
    };

    // Build trend data per marker
    const allMarkerNames = Array.from(new Set(tests.flatMap((t) => (t.markers || []).map((m) => m.name)))).slice(0, 6);
    const trendData = (name) => tests
        .slice()
        .sort((a, b) => a.date.localeCompare(b.date))
        .map((t) => {
            const m = (t.markers || []).find((x) => x.name === name);
            return { date: t.date, value: m ? m.value : null };
        })
        .filter((p) => p.value !== null);

    return (
        <div className="max-w-5xl mx-auto fade-up" data-testid="blood-root">
            <div className="label-eyebrow">Blood tests</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Watch your liver heal.</h1>

            <Tabs defaultValue="add" className="mt-10">
                <TabsList className="rounded-full bg-secondary p-1">
                    <TabsTrigger value="add" data-testid="tab-add" className="rounded-full px-6">Add result</TabsTrigger>
                    <TabsTrigger value="trends" data-testid="tab-trends" className="rounded-full px-6">Trends</TabsTrigger>
                    <TabsTrigger value="history" data-testid="tab-history" className="rounded-full px-6">History</TabsTrigger>
                </TabsList>

                <TabsContent value="add" className="mt-6">
                    <form onSubmit={save} className="tactile-card p-6 sm:p-8 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="label-eyebrow">Date</label>
                                <Input data-testid="blood-date-input" type="date" value={date} onChange={(e) => setDate(e.target.value)} className="mt-1" />
                            </div>
                            <div className="md:col-span-2">
                                <label className="label-eyebrow">Lab / clinic</label>
                                <Input data-testid="blood-lab-input" value={lab} onChange={(e) => setLab(e.target.value)} placeholder="optional" className="mt-1" />
                            </div>
                        </div>

                        <div>
                            <label className="cursor-pointer inline-flex items-center gap-2 text-sm text-primary font-medium border border-dashed border-primary/50 rounded-2xl px-4 py-3 hover:bg-primary/5 transition-colors" data-testid="blood-extract-label">
                                {extracting ? <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} /> : <Upload className="w-4 h-4" strokeWidth={1.5} />}
                                {extracting ? "Extracting…" : "Upload report image (AI will fill the form)"}
                                <input
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    data-testid="blood-extract-input"
                                    onChange={(e) => onExtract(e.target.files?.[0])}
                                />
                            </label>
                        </div>

                        <div>
                            <div className="flex items-center justify-between mb-3">
                                <div className="label-eyebrow">Markers</div>
                                <button type="button" onClick={addMarker} data-testid="blood-add-marker" className="text-xs inline-flex items-center gap-1 text-primary">
                                    <Plus className="w-3.5 h-3.5" strokeWidth={1.5} /> Add row
                                </button>
                            </div>
                            <div className="space-y-2">
                                {markers.map((m, i) => (
                                    <div key={i} className="grid grid-cols-12 gap-2 items-center" data-testid={`marker-row-${i}`}>
                                        <Input className="col-span-4" placeholder="Name" value={m.name} onChange={(e) => setMarker(i, "name", e.target.value)} />
                                        <Input className="col-span-3" type="number" step="0.01" placeholder="Value" value={m.value} onChange={(e) => setMarker(i, "value", e.target.value)} />
                                        <Input className="col-span-2" placeholder="Unit" value={m.unit} onChange={(e) => setMarker(i, "unit", e.target.value)} />
                                        <Input className="col-span-2" placeholder="Range" value={m.reference_range} onChange={(e) => setMarker(i, "reference_range", e.target.value)} />
                                        <button type="button" onClick={() => removeMarker(i)} className="text-muted-foreground hover:text-destructive col-span-1 flex justify-center">
                                            <X className="w-4 h-4" strokeWidth={1.5} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="label-eyebrow">Notes</label>
                            <Textarea data-testid="blood-notes-input" value={notes} onChange={(e) => setNotes(e.target.value)} className="mt-2 rounded-2xl" />
                        </div>

                        <Button type="submit" disabled={submitting} data-testid="blood-submit-btn" className="rounded-full px-8">
                            {submitting ? "Saving…" : "Save result"}
                        </Button>
                    </form>
                </TabsContent>

                <TabsContent value="trends" className="mt-6">
                    {tests.length < 2 && (
                        <div className="tactile-card p-8 text-sm text-muted-foreground">Add 2+ results to see trends.</div>
                    )}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        {allMarkerNames.map((name) => {
                            const data = trendData(name);
                            if (data.length < 2) return null;
                            return (
                                <div key={name} className="tactile-card p-5" data-testid={`trend-${name}`}>
                                    <div className="label-eyebrow">{name}</div>
                                    <div className="h-48 mt-2">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: -16 }}>
                                                <CartesianGrid stroke="hsl(42 20% 90%)" strokeDasharray="2 4" />
                                                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "hsl(127 4% 36%)" }} />
                                                <YAxis tick={{ fontSize: 10, fill: "hsl(127 4% 36%)" }} />
                                                <Tooltip contentStyle={{ background: "hsl(127 9% 19%)", border: "none", borderRadius: 12, color: "#fff" }} />
                                                <Line type="monotone" dataKey="value" stroke="hsl(136 18% 35%)" strokeWidth={2} dot={{ r: 3, fill: "hsl(13 54% 55%)" }} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </TabsContent>

                <TabsContent value="history" className="mt-6 space-y-3">
                    {tests.length === 0 && <div className="text-sm text-muted-foreground">No results yet.</div>}
                    {tests.map((t) => (
                        <div key={t.id} className="tactile-card p-5" data-testid={`blood-row-${t.id}`}>
                            <div className="flex items-start justify-between">
                                <div>
                                    <div className="font-display text-lg font-medium tracking-tight">
                                        {new Date(t.date).toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })}
                                    </div>
                                    {t.lab && <div className="text-xs text-muted-foreground mt-0.5">{t.lab}</div>}
                                </div>
                                <button onClick={() => remove(t.id)} className="text-muted-foreground hover:text-destructive">
                                    <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                                </button>
                            </div>
                            <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-2">
                                {(t.markers || []).map((m, i) => (
                                    <div key={i} className="text-sm">
                                        <span className="text-muted-foreground">{m.name}:</span>{" "}
                                        <span className="font-medium">{m.value}{m.unit && ` ${m.unit}`}</span>
                                        {m.reference_range && <span className="text-xs text-muted-foreground"> ({m.reference_range})</span>}
                                    </div>
                                ))}
                            </div>
                            {t.notes && <p className="mt-3 text-sm text-muted-foreground">{t.notes}</p>}
                        </div>
                    ))}
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default BloodTests;
