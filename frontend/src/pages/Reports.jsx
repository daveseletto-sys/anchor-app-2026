import React, { useState } from "react";
import { BACKEND_URL } from "../lib/api";
import { Button } from "../components/ui/button";
import { Download, FileText, Stethoscope, NotebookPen, Loader2 } from "lucide-react";
import { toast } from "sonner";

const SCOPES = [
    { value: "clinical", label: "Clinical", icon: Stethoscope, desc: "Stats, blood markers, medications, goals. No diary entries. Best for doctor visits." },
    { value: "full", label: "Full", icon: FileText, desc: "Everything: stats + blood + meds + goals + diary entries. Best for therapists." },
    { value: "personal", label: "Personal", icon: NotebookPen, desc: "Stats + diary entries. Best for sponsors or self-reflection." },
];

const Reports = () => {
    const [period, setPeriod] = useState("week");
    const [scope, setScope] = useState("clinical");
    const [downloading, setDownloading] = useState(false);

    const download = async () => {
        setDownloading(true);
        try {
            const token = localStorage.getItem("anchor_token");
            const res = await fetch(`${BACKEND_URL}/api/reports/pdf?period=${period}&scope=${scope}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) {
                let detail = "Could not generate report";
                try { detail = (await res.json()).detail || detail; } catch (_) { /* ignore */ }
                throw new Error(detail);
            }
            const disposition = res.headers.get("Content-Disposition") || "";
            const match = disposition.match(/filename="?([^";]+)"?/i);
            const filename = match ? match[1] : `anchor-report-${period}-${scope}.pdf`;
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
            toast.success("Report downloaded");
        } catch (err) {
            toast.error(err.message || "Could not download");
        } finally {
            setDownloading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto fade-up" data-testid="reports-root">
            <div className="label-eyebrow">Reports</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Export a PDF.</h1>
            <p className="text-muted-foreground mt-3">For your doctor, therapist, sponsor — or just to keep a record.</p>

            <div className="tactile-card p-6 sm:p-8 mt-10">
                <div className="label-eyebrow mb-3">Time period</div>
                <div className="grid grid-cols-2 gap-3">
                    {[{ v: "week", l: "Last 7 days" }, { v: "month", l: "Last 30 days" }].map((p) => (
                        <button
                            key={p.v}
                            type="button"
                            onClick={() => setPeriod(p.v)}
                            data-testid={`period-${p.v}`}
                            className={`rounded-2xl border p-4 text-left transition-colors ${
                                period === p.v ? "border-primary bg-primary/5" : "border-border hover:bg-secondary"
                            }`}
                        >
                            <div className="font-display font-medium tracking-tight">{p.l}</div>
                        </button>
                    ))}
                </div>

                <div className="label-eyebrow mt-8 mb-3">Report scope</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {SCOPES.map((s) => {
                        const Icon = s.icon;
                        const active = scope === s.value;
                        return (
                            <button
                                key={s.value}
                                type="button"
                                onClick={() => setScope(s.value)}
                                data-testid={`scope-${s.value}`}
                                className={`rounded-2xl border p-4 text-left transition-colors ${
                                    active ? "border-primary bg-primary/5" : "border-border hover:bg-secondary"
                                }`}
                            >
                                <Icon className="w-5 h-5 text-primary mb-2" strokeWidth={1.5} />
                                <div className="font-display font-medium tracking-tight">{s.label}</div>
                                <div className="text-xs text-muted-foreground mt-2 leading-relaxed">{s.desc}</div>
                            </button>
                        );
                    })}
                </div>

                <div className="mt-8 flex items-center justify-between flex-wrap gap-4">
                    <div className="text-xs text-muted-foreground max-w-md">
                        Self-reported summary. Not a substitute for clinical assessment.
                    </div>
                    <Button onClick={download} disabled={downloading} data-testid="download-pdf-btn" className="rounded-full px-7">
                        {downloading ? (
                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" strokeWidth={1.5} /> Generating…</>
                        ) : (
                            <><Download className="w-4 h-4 mr-2" strokeWidth={1.5} /> Download PDF</>
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default Reports;
