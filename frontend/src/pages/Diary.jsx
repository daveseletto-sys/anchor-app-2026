import React, { useEffect, useState } from "react";
import { api, todayStr } from "../lib/api";
import { Slider } from "../components/ui/slider";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { toast } from "sonner";
import { Trash2 } from "lucide-react";

const MOODS = ["Calm", "Hopeful", "Tired", "Anxious", "Craving", "Strong", "Lonely", "Grateful", "Restless", "Focused"];

const Diary = () => {
    const [entries, setEntries] = useState([]);
    const [rating, setRating] = useState([7]);
    const [tags, setTags] = useState([]);
    const [notes, setNotes] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const load = async () => {
        const { data } = await api.get("/diary");
        setEntries(data);
    };

    useEffect(() => {
        load();
    }, []);

    const toggleTag = (t) => {
        setTags((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]));
    };

    const submit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await api.post("/diary", { date: todayStr(), rating: rating[0], mood_tags: tags, notes });
            toast.success("Saved today's check-in");
            setNotes("");
            setTags([]);
            await load();
        } catch (err) {
            toast.error(err?.response?.data?.detail || "Could not save");
        } finally {
            setSubmitting(false);
        }
    };

    const remove = async (id) => {
        await api.delete(`/diary/${id}`);
        await load();
    };

    return (
        <div className="max-w-3xl mx-auto fade-up" data-testid="diary-root">
            <div className="label-eyebrow">Daily diary</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">How did today feel?</h1>
            <p className="text-muted-foreground mt-3">No judgment. Just a quiet record of the day.</p>

            <form onSubmit={submit} className="tactile-card p-6 sm:p-8 mt-8 space-y-8">
                <div>
                    <div className="flex items-end justify-between">
                        <label className="label-eyebrow">Rating</label>
                        <div className="font-display text-3xl font-medium tracking-tight" data-testid="rating-value">
                            {rating[0]}<span className="text-base text-muted-foreground">/10</span>
                        </div>
                    </div>
                    <Slider
                        data-testid="rating-slider"
                        value={rating}
                        onValueChange={setRating}
                        min={1}
                        max={10}
                        step={1}
                        className="mt-4"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-2">
                        <span>Rough day</span>
                        <span>Great day</span>
                    </div>
                </div>

                <div>
                    <label className="label-eyebrow">Mood</label>
                    <div className="flex flex-wrap gap-2 mt-3">
                        {MOODS.map((m) => (
                            <button
                                type="button"
                                key={m}
                                data-testid={`mood-tag-${m.toLowerCase()}`}
                                onClick={() => toggleTag(m)}
                                className={`text-sm px-4 py-1.5 rounded-full border transition-colors ${
                                    tags.includes(m)
                                        ? "bg-primary text-primary-foreground border-primary"
                                        : "bg-transparent text-foreground border-border hover:bg-secondary"
                                }`}
                            >
                                {m}
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="label-eyebrow">Notes</label>
                    <Textarea
                        data-testid="diary-notes-input"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="What happened today? Triggers, wins, what helped…"
                        className="mt-3 min-h-32 rounded-2xl"
                    />
                </div>

                <Button type="submit" disabled={submitting} data-testid="diary-submit-btn" className="rounded-full px-8">
                    {submitting ? "Saving…" : "Save check-in"}
                </Button>
            </form>

            <h2 className="font-display text-2xl font-medium tracking-tight mt-12 mb-4">Past entries</h2>
            <div className="space-y-3">
                {entries.length === 0 && <div className="text-sm text-muted-foreground">No entries yet.</div>}
                {entries.map((e) => (
                    <div key={e.id} className="tactile-card p-5" data-testid={`diary-entry-${e.id}`}>
                        <div className="flex items-start justify-between gap-4">
                            <div>
                                <div className="text-sm text-muted-foreground">
                                    {new Date(e.date).toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}
                                </div>
                                <div className="font-display text-2xl font-medium tracking-tight mt-1">
                                    {e.rating}<span className="text-sm text-muted-foreground">/10</span>
                                </div>
                            </div>
                            <button onClick={() => remove(e.id)} data-testid={`diary-delete-${e.id}`} className="text-muted-foreground hover:text-destructive transition-colors">
                                <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                            </button>
                        </div>
                        {e.mood_tags?.length > 0 && (
                            <div className="flex flex-wrap gap-1.5 mt-3">
                                {e.mood_tags.map((t) => (
                                    <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-primary/10 text-primary">{t}</span>
                                ))}
                            </div>
                        )}
                        {e.notes && <p className="mt-3 text-sm leading-relaxed whitespace-pre-wrap">{e.notes}</p>}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Diary;
