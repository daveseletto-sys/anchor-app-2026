import React, { useEffect, useState } from "react";
import { api, BACKEND_URL } from "../lib/api";
import { Button } from "../components/ui/button";
import { Trash2, Copy, Link2, Check, Clock, AlertCircle } from "lucide-react";
import { toast } from "sonner";

const buildShareUrl = (token) => `${window.location.origin}/share/${token}`;

const ShareLinks = () => {
    const [links, setLinks] = useState([]);
    const [scope, setScope] = useState("summary");
    const [days, setDays] = useState(7);
    const [creating, setCreating] = useState(false);
    const [copiedId, setCopiedId] = useState(null);

    const load = async () => {
        const { data } = await api.get("/share-links");
        setLinks(data);
    };

    useEffect(() => {
        load();
    }, []);

    const create = async () => {
        setCreating(true);
        try {
            await api.post("/share-links", { expires_in_days: days, scope });
            toast.success("Share link created");
            await load();
        } catch (err) {
            toast.error(err?.response?.data?.detail || "Could not create");
        } finally {
            setCreating(false);
        }
    };

    const copy = async (link) => {
        try {
            await navigator.clipboard.writeText(buildShareUrl(link.token));
            setCopiedId(link.id);
            toast.success("Link copied to clipboard");
            setTimeout(() => setCopiedId(null), 2000);
        } catch (err) {
            toast.error("Could not copy — please copy manually");
        }
    };

    const revoke = async (id) => {
        await api.delete(`/share-links/${id}`);
        toast.success("Link revoked");
        await load();
    };

    const isExpired = (l) => new Date(l.expires_at) < new Date();
    const isActive = (l) => !l.revoked && !isExpired(l);

    return (
        <div className="max-w-3xl mx-auto fade-up" data-testid="share-root">
            <div className="label-eyebrow">Share with a sponsor</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">A trusted link.</h1>
            <p className="text-muted-foreground mt-3 max-w-2xl">
                Generate a private, read-only link to share your progress with a sponsor, partner, or coach. Anyone with the link can view — no signup needed. You can revoke it any time.
            </p>

            <div className="tactile-card p-6 sm:p-8 mt-10" data-testid="share-create-card">
                <div className="label-eyebrow mb-3">What to share</div>
                <div className="grid grid-cols-2 gap-3">
                    <button
                        type="button"
                        onClick={() => setScope("summary")}
                        data-testid="share-scope-summary"
                        className={`rounded-2xl border p-4 text-left transition-colors ${
                            scope === "summary" ? "border-primary bg-primary/5" : "border-border hover:bg-secondary"
                        }`}
                    >
                        <div className="font-display font-medium tracking-tight">Summary</div>
                        <div className="text-xs text-muted-foreground mt-2 leading-relaxed">Streak, diet averages, weekly goals, mood average. No diary entries.</div>
                    </button>
                    <button
                        type="button"
                        onClick={() => setScope("full")}
                        data-testid="share-scope-full"
                        className={`rounded-2xl border p-4 text-left transition-colors ${
                            scope === "full" ? "border-primary bg-primary/5" : "border-border hover:bg-secondary"
                        }`}
                    >
                        <div className="font-display font-medium tracking-tight">Full</div>
                        <div className="text-xs text-muted-foreground mt-2 leading-relaxed">Summary plus the last 7 days of diary check-ins (date, rating, mood tags).</div>
                    </button>
                </div>

                <div className="label-eyebrow mt-6 mb-3">Expires after</div>
                <div className="flex gap-2 flex-wrap">
                    {[1, 3, 7, 14, 30].map((d) => (
                        <button
                            key={d}
                            type="button"
                            onClick={() => setDays(d)}
                            data-testid={`share-days-${d}`}
                            className={`text-sm px-4 py-2 rounded-full border transition-colors ${
                                days === d
                                    ? "bg-primary text-primary-foreground border-primary"
                                    : "bg-transparent text-foreground border-border hover:bg-secondary"
                            }`}
                        >
                            {d === 1 ? "1 day" : `${d} days`}
                        </button>
                    ))}
                </div>

                <Button onClick={create} disabled={creating} data-testid="share-create-btn" className="rounded-full px-7 mt-6">
                    <Link2 className="w-4 h-4 mr-2" strokeWidth={1.5} />
                    {creating ? "Creating…" : "Create link"}
                </Button>
            </div>

            <h2 className="font-display text-2xl font-medium tracking-tight mt-12 mb-4">Your links</h2>
            <div className="space-y-3">
                {links.length === 0 && <div className="text-sm text-muted-foreground">No links yet.</div>}
                {links.map((l) => {
                    const expired = isExpired(l);
                    const active = isActive(l);
                    return (
                        <div key={l.id} className={`tactile-card p-5 ${active ? "" : "opacity-60"}`} data-testid={`share-link-${l.id}`}>
                            <div className="flex items-start justify-between gap-4 flex-wrap">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <div className="font-display font-medium tracking-tight">{l.scope === "full" ? "Full" : "Summary"}</div>
                                        {active && <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">Active</span>}
                                        {l.revoked && <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">Revoked</span>}
                                        {expired && !l.revoked && <span className="text-xs px-2 py-0.5 rounded-full bg-accent/15 text-accent">Expired</span>}
                                    </div>
                                    <code className="block mt-2 text-xs text-muted-foreground break-all" data-testid={`share-url-${l.id}`}>{buildShareUrl(l.token)}</code>
                                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" strokeWidth={1.5} />
                                            Expires {new Date(l.expires_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    {active && (
                                        <button onClick={() => copy(l)} data-testid={`share-copy-${l.id}`} className="text-xs inline-flex items-center gap-1 text-primary border border-primary/30 rounded-full px-3 py-1.5 hover:bg-primary/5">
                                            {copiedId === l.id ? <Check className="w-3.5 h-3.5" strokeWidth={1.5} /> : <Copy className="w-3.5 h-3.5" strokeWidth={1.5} />}
                                            {copiedId === l.id ? "Copied" : "Copy"}
                                        </button>
                                    )}
                                    {!l.revoked && (
                                        <button onClick={() => revoke(l.id)} data-testid={`share-revoke-${l.id}`} className="text-muted-foreground hover:text-destructive">
                                            <Trash2 className="w-4 h-4" strokeWidth={1.5} />
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="mt-10 p-5 rounded-2xl border border-dashed border-border text-xs text-muted-foreground flex items-start gap-2">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" strokeWidth={1.5} />
                <span>Anyone who has the link can view your shared data until it expires or you revoke it. Don't post these links publicly.</span>
            </div>
        </div>
    );
};

export default ShareLinks;
