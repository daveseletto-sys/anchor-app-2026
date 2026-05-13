import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Anchor, Heart, Activity, BookOpen, Camera, Target } from "lucide-react";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";

const HERO_BG = "https://images.unsplash.com/photo-1512230254992-9788b9bbc69c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NjZ8MHwxfHNlYXJjaHwzfHxzdW5yaXNlJTIwbW91bnRhaW5zJTIwY2FsbXxlbnwwfHx8fDE3Nzg2NDczMzJ8MA&ixlib=rb-4.1.0&q=85";

const FEATURES = [
    { icon: Heart, title: "Daily reflection", body: "Rate your day 1–10 with mood tags and a private journal." },
    { icon: Activity, title: "Diet that supports recovery", body: "Track protein, salt, and water against recovery-friendly targets." },
    { icon: Camera, title: "AI food label reader", body: "Snap a label — get nutrition data extracted instantly." },
    { icon: BookOpen, title: "Blood test trends", body: "Log ALT, AST, GGT and watch your liver markers heal over time." },
    { icon: Target, title: "Weekly goals", body: "Small, meaningful commitments — one week at a time." },
    { icon: Anchor, title: "Sobriety streak", body: "A quiet, steady counter for the days you've shown up for yourself." },
];

const Landing = () => {
    const { login, register } = useAuth();
    const navigate = useNavigate();
    const [mode, setMode] = useState("login");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [name, setName] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            if (mode === "login") {
                await login(email, password);
            } else {
                await register(email, password, name || email.split("@")[0]);
            }
            toast.success("Welcome back");
            navigate("/app");
        } catch (err) {
            toast.error(err?.response?.data?.detail || "Something went wrong");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-5">
            {/* Left: hero image + quote */}
            <div className="relative lg:col-span-3 min-h-[40vh] lg:min-h-screen overflow-hidden">
                <img src={HERO_BG} alt="Mountain sunrise" className="absolute inset-0 w-full h-full object-cover" />
                <div className="absolute inset-0 bg-black/35" />
                <div className="relative z-10 h-full flex flex-col justify-between p-8 md:p-14 text-white">
                    <div className="flex items-center gap-2">
                        <Anchor className="w-6 h-6" strokeWidth={1.5} />
                        <span className="font-display font-semibold text-lg tracking-tight">Anchor</span>
                    </div>
                    <div className="max-w-xl">
                        <div className="label-eyebrow !text-white/70 mb-4">A recovery companion</div>
                        <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-light tracking-tight leading-[1.05]">
                            One steady day,<br />
                            then another.
                        </h1>
                        <p className="mt-6 text-white/80 max-w-md font-body text-base sm:text-lg">
                            Track the small things that rebuild a body — protein, hydration, salt, sleep, mood — and watch your liver markers and your days tell a story of healing.
                        </p>
                    </div>
                    <div className="text-white/60 text-sm">
                        "Recovery is not a straight line. It's a thousand small returns home."
                    </div>
                </div>
            </div>

            {/* Right: auth */}
            <div className="lg:col-span-2 flex items-center justify-center p-6 sm:p-10 md:p-14 bg-background">
                <div className="w-full max-w-md fade-up">
                    <div className="label-eyebrow mb-2">{mode === "login" ? "Welcome back" : "Begin"}</div>
                    <h2 className="font-display text-3xl sm:text-4xl font-medium tracking-tight">
                        {mode === "login" ? "Sign in to Anchor" : "Create your account"}
                    </h2>
                    <p className="text-muted-foreground mt-2 text-sm">
                        {mode === "login" ? "Pick up where you left off." : "It takes less than a minute."}
                    </p>

                    <form onSubmit={handleSubmit} className="mt-10 space-y-6">
                        {mode === "register" && (
                            <div>
                                <label className="label-eyebrow block mb-2">Name</label>
                                <input
                                    data-testid="register-name-input"
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Your first name"
                                    className="w-full bg-transparent border-b-2 border-border h-12 focus:outline-none focus:border-primary transition-colors"
                                />
                            </div>
                        )}
                        <div>
                            <label className="label-eyebrow block mb-2">Email</label>
                            <input
                                data-testid="auth-email-input"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@example.com"
                                className="w-full bg-transparent border-b-2 border-border h-12 focus:outline-none focus:border-primary transition-colors"
                            />
                        </div>
                        <div>
                            <label className="label-eyebrow block mb-2">Password</label>
                            <input
                                data-testid="auth-password-input"
                                type="password"
                                required
                                minLength={6}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="At least 6 characters"
                                className="w-full bg-transparent border-b-2 border-border h-12 focus:outline-none focus:border-primary transition-colors"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={submitting}
                            data-testid="auth-submit-btn"
                            className="anchor-btn-primary w-full mt-4 disabled:opacity-60"
                        >
                            {submitting ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
                        </button>
                    </form>

                    <div className="mt-8 text-sm text-muted-foreground">
                        {mode === "login" ? (
                            <>
                                New here?{" "}
                                <button data-testid="switch-to-register" onClick={() => setMode("register")} className="text-primary font-medium underline-offset-4 hover:underline">
                                    Create an account
                                </button>
                            </>
                        ) : (
                            <>
                                Already have an account?{" "}
                                <button data-testid="switch-to-login" onClick={() => setMode("login")} className="text-primary font-medium underline-offset-4 hover:underline">
                                    Sign in
                                </button>
                            </>
                        )}
                    </div>

                    <div className="mt-16 grid grid-cols-2 gap-4">
                        {FEATURES.slice(0, 4).map((f, i) => {
                            const Icon = f.icon;
                            return (
                                <div key={i} className="text-xs text-muted-foreground">
                                    <Icon className="w-4 h-4 text-primary mb-2" strokeWidth={1.5} />
                                    <div className="font-medium text-foreground">{f.title}</div>
                                    <div className="mt-1 leading-relaxed">{f.body}</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Landing;
