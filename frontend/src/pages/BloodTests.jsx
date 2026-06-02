import React, { useEffect, useState } from "react";
import { api, imageFileToJpegBase64, todayStr } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import { Trash2, Upload, Loader2, Plus, X, FileText } from "lucide-react";
import { toast } from "sonner";

const Documents = () => {
    const [tests, setTests] = useState([]);
    const [date, setDate] = useState(todayStr());
    const [lab, setLab] = useState("");
    const [notes, setNotes] = useState("");
    const [markers, setMarkers] = useState([{ name: "", value: "", unit: "", reference_range: "" }]);
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
                    reference_range: "",
                })));
                toast.success(`Transcribed ${found.length} line${found.length === 1 ? "" : "s"} — review before saving`);
            } else {
                toast.message("Couldn't read text from that photo", {
                    description: "Try a clearer, well-lit photo, or type the details below.",
                });
            }
        } catch (err) {
            toast.error(err?.response?.data?.detail || err?.message || "Could not scan");
        } finally {
            setExtracting(false);
        }
    };

    const save = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            const clean = markers
                .filter((m) => m.name)
                .map((m) => ({
                    name: m.name,
                    value: parseFloat(m.value) || 0,
                    unit: m.unit || "",
                    reference_range: "",
                }));
            await api.post("/blood-tests", { date, lab, markers: clean, notes });
            toast.success("Document saved to your private journal");
            setMarkers([{ name: "", value: "", unit: "", reference_range: "" }]);
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

    return (
        <div className="max-w-5xl mx-auto fade-up" data-testid="documents-root">
            <div className="label-eyebrow">Documents</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Keep notes for your doctor.</h1>
            <p className="text-sm text-muted-foreground mt-3 max-w-2xl leading-relaxed">
                A private place to keep transcriptions of any documents you want to bring up with your doctor — letters, results, notes, blood pressure logs, anything paper. Anchor doesn't interpret these for you. It just helps you store them.
            </p>

            <div className="tactile-card p-4 mt-6 flex gap-3 items-start bg-secondary/30">
                <FileText className="w-4 h-4 mt-0.5 text-muted-foreground" strokeWidth={1.5} />
                <p className="text-xs text-muted-foreground leading-relaxed">
                    <strong>Anchor is not a medical app.</strong> Nothing here is medical advice. Always speak with your doctor about any health information or document.
                </p>
            </div>

            <Tabs defaultValue="add" className="mt-8">
                <TabsList className="rounded-full bg-secondary p-1">
                    <TabsTrigger value="add" data-testid="tab-add" className="rounded-full px-6">Add document</TabsTrigger>
                    <TabsTrigger value="history" data-testid="tab-history" className="rounded-full px-6">History</TabsTrigger>
                </TabsList>

                <TabsContent value="add" className="mt-6">
                    <form onSubmit={save} className="tactile-card p-6 sm:p-8 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="label-eyebrow">Date on document</label>
                                <Input data-testid="blood-date-input" type="date" value={date} onChange={(e) => setDate(e.target.value)} className="mt-1" />
                            </div>
                            <div className="md:col-span-2">
                                <label className="label-eyebrow">Source / issuer</label>
                                <Input data-testid="blood-lab-input" value={lab} onChange={(e) => setLab(e.target.value)} placeholder="e.g. Letter from Dr Smith, GP visit notes (optional)" className="mt-1" />
                            </div>
                        </div>

                        <div>
                            <label className="cursor-pointer inline-flex items-center gap-2 text-sm text-primary font-medium border border-dashed border-primary/50 rounded-2xl px-4 py-3 hover:bg-primary/5 transition-colors" data-testid="blood-extract-label">
                                {extracting ? <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} /> : <Upload className="w-4 h-4" strokeWidth={1.5} />}
                                {extracting ? "Reading…" : "Scan a document photo (we'll transcribe the text)"}
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
                                <div className="label-eyebrow">Labelled values from the document</div>
                                <button type="button" onClick={addMarker} data-testid="blood-add-marker" className="text-xs inline-flex items-center gap-1 text-primary">
                                    <Plus className="w-3.5 h-3.5" strokeWidth={1.5} /> Add row
                                </button>
                            </div>
                            <p className="text-xs text-muted-foreground mb-3">Optional. Just a place to transcribe lines like "Weight 78 kg" or "Blood pressure 122/78" so you have them for reference.</p>
                            <div className="space-y-2">
                                {markers.map((m, i) => (
                                    <div key={i} className="grid grid-cols-12 gap-2 items-center" data-testid={`marker-row-${i}`}>
                                        <Input className="col-span-5" placeholder="Label (e.g. Weight)" value={m.name} onChange={(e) => setMarker(i, "name", e.target.value)} />
                                        <Input className="col-span-3" type="number" step="0.01" placeholder="Value" value={m.value} onChange={(e) => setMarker(i, "value", e.target.value)} />
                                        <Input className="col-span-3" placeholder="Unit" value={m.unit} onChange={(e) => setMarker(i, "unit", e.target.value)} />
                                        <button type="button" onClick={() => removeMarker(i)} className="text-muted-foreground hover:text-destructive col-span-1 flex justify-center">
                                            <X className="w-4 h-4" strokeWidth={1.5} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="label-eyebrow">Your notes</label>
                            <Textarea data-testid="blood-notes-input" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Anything you want to remember to ask your doctor about this document…" className="mt-2 rounded-2xl" />
                        </div>

                        <Button type="submit" disabled={submitting} data-testid="blood-submit-btn" className="rounded-full px-8">
                            {submitting ? "Saving…" : "Save document"}
                        </Button>
                    </form>
                </TabsContent>

                <TabsContent value="history" className="mt-6 space-y-3">
                    {tests.length === 0 && <div className="text-sm text-muted-foreground">No documents yet.</div>}
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
                                    </div>
                                ))}
                            </div>
                            {t.notes && <p className="mt-3 text-sm text-muted-foreground whitespace-pre-wrap">{t.notes}</p>}
                        </div>
                    ))}
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default Documents;
