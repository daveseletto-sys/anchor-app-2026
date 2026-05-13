import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import { Save, KeyRound } from "lucide-react";

const Profile = () => {
    const { user, setUser } = useAuth();
    const [form, setForm] = useState({ name: "", sobriety_start: "", height_cm: "", weight_kg: "", region: "" });
    const [pwForm, setPwForm] = useState({ current_password: "", new_password: "" });
    const [saving, setSaving] = useState(false);
    const [changingPw, setChangingPw] = useState(false);

    useEffect(() => {
        if (user) {
            setForm({
                name: user.name || "",
                sobriety_start: user.sobriety_start || "",
                height_cm: user.height_cm ?? "",
                weight_kg: user.weight_kg ?? "",
                region: user.region || "",
            });
        }
    }, [user]);

    const setField = (k, v) => setForm((p) => ({ ...p, [k]: v }));

    const save = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            const payload = {
                name: form.name || null,
                sobriety_start: form.sobriety_start || null,
                height_cm: form.height_cm === "" ? null : parseFloat(form.height_cm),
                weight_kg: form.weight_kg === "" ? null : parseFloat(form.weight_kg),
                region: form.region,
            };
            const { data } = await api.patch("/users/me", payload);
            setUser(data);
            toast.success("Profile saved");
        } catch (err) {
            toast.error(err?.response?.data?.detail || "Could not save");
        } finally {
            setSaving(false);
        }
    };

    const changePw = async (e) => {
        e.preventDefault();
        if (pwForm.new_password.length < 6) {
            toast.error("New password must be at least 6 characters");
            return;
        }
        setChangingPw(true);
        try {
            await api.post("/auth/change-password", pwForm);
            toast.success("Password updated");
            setPwForm({ current_password: "", new_password: "" });
        } catch (err) {
            toast.error(err?.response?.data?.detail || "Could not update password");
        } finally {
            setChangingPw(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto fade-up" data-testid="profile-root">
            <div className="label-eyebrow">Profile</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Your details.</h1>

            <form onSubmit={save} className="tactile-card p-6 sm:p-8 mt-10 space-y-6">
                <div>
                    <label className="label-eyebrow">Name</label>
                    <Input data-testid="profile-name" value={form.name} onChange={(e) => setField("name", e.target.value)} className="mt-2" />
                </div>
                <div>
                    <label className="label-eyebrow">Email</label>
                    <Input value={user?.email || ""} disabled className="mt-2 opacity-60" />
                </div>
                <div>
                    <label className="label-eyebrow">Sobriety start date</label>
                    <Input data-testid="profile-sobriety" type="date" value={form.sobriety_start || ""} onChange={(e) => setField("sobriety_start", e.target.value)} className="mt-2" />
                    <div className="text-xs text-muted-foreground mt-2">The day your streak counts from.</div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="label-eyebrow">Height (cm)</label>
                        <Input data-testid="profile-height" type="number" value={form.height_cm} onChange={(e) => setField("height_cm", e.target.value)} className="mt-2" />
                    </div>
                    <div>
                        <label className="label-eyebrow">Weight (kg)</label>
                        <Input data-testid="profile-weight" type="number" value={form.weight_kg} onChange={(e) => setField("weight_kg", e.target.value)} className="mt-2" />
                    </div>
                </div>
                <div>
                    <label className="label-eyebrow">Region</label>
                    <div className="flex gap-2 mt-2">
                        {[{ v: "", l: "Both" }, { v: "US", l: "United States" }, { v: "UK", l: "United Kingdom" }].map((r) => (
                            <button
                                type="button"
                                key={r.v || "both"}
                                onClick={() => setField("region", r.v)}
                                data-testid={`region-${r.v || "both"}`}
                                className={`text-sm px-4 py-2 rounded-full border transition-colors ${
                                    form.region === r.v
                                        ? "bg-primary text-primary-foreground border-primary"
                                        : "bg-transparent text-foreground border-border hover:bg-secondary"
                                }`}
                            >
                                {r.l}
                            </button>
                        ))}
                    </div>
                    <div className="text-xs text-muted-foreground mt-2">Filters the crisis hotlines we show you.</div>
                </div>
                <Button type="submit" disabled={saving} data-testid="profile-save-btn" className="rounded-full px-7">
                    <Save className="w-4 h-4 mr-1.5" strokeWidth={1.5} /> {saving ? "Saving…" : "Save changes"}
                </Button>
            </form>

            <form onSubmit={changePw} className="tactile-card p-6 sm:p-8 mt-6 space-y-5" data-testid="password-form">
                <div className="flex items-center gap-2">
                    <KeyRound className="w-4 h-4 text-primary" strokeWidth={1.5} />
                    <h2 className="font-display text-xl font-medium tracking-tight">Change password</h2>
                </div>
                <div>
                    <label className="label-eyebrow">Current password</label>
                    <Input data-testid="pw-current" type="password" value={pwForm.current_password} onChange={(e) => setPwForm((p) => ({ ...p, current_password: e.target.value }))} className="mt-2" />
                </div>
                <div>
                    <label className="label-eyebrow">New password</label>
                    <Input data-testid="pw-new" type="password" value={pwForm.new_password} onChange={(e) => setPwForm((p) => ({ ...p, new_password: e.target.value }))} className="mt-2" />
                </div>
                <Button type="submit" disabled={changingPw} data-testid="pw-submit" variant="outline" className="rounded-full px-6">
                    {changingPw ? "Updating…" : "Update password"}
                </Button>
            </form>
        </div>
    );
};

export default Profile;
