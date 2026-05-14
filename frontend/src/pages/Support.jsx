import React from "react";
import { Link } from "react-router-dom";
import { Anchor, Mail, LifeBuoy, BookOpen, ShieldCheck, FileDown, Share2 } from "lucide-react";

const Faq = ({ q, children }) => (
    <details className="tactile-card p-5 sm:p-6 group" data-testid={`faq-${q.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 40)}`}>
        <summary className="cursor-pointer font-display text-base font-medium tracking-tight list-none flex items-center justify-between">
            <span>{q}</span>
            <span className="text-muted-foreground group-open:rotate-45 transition-transform text-xl leading-none">+</span>
        </summary>
        <div className="mt-3 text-sm text-foreground/85 leading-relaxed space-y-2">{children}</div>
    </details>
);

const Support = () => (
    <div className="min-h-screen bg-background p-6 sm:p-12 fade-up" data-testid="support-root">
        <div className="max-w-3xl mx-auto">
            <Link to="/" className="flex items-center gap-2 mb-8">
                <Anchor className="w-5 h-5 text-primary" strokeWidth={1.5} />
                <span className="font-display font-semibold tracking-tight">Anchor</span>
            </Link>

            <div className="label-eyebrow">Support</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">We're here to help.</h1>
            <p className="text-muted-foreground mt-3 max-w-2xl">
                Quick answers below. If you can't find what you need, email us at <a className="text-primary underline" href="mailto:support@anchorhelp.com.au">support@anchorhelp.com.au</a> — we usually respond within one business day.
            </p>

            {/* Crisis banner */}
            <div className="tactile-card p-5 mt-8 bg-[hsl(13_54%_96%)] border-[hsl(13_54%_85%)]" data-testid="support-crisis-banner">
                <div className="flex items-start gap-3">
                    <LifeBuoy className="w-5 h-5 text-accent mt-0.5" strokeWidth={1.5} />
                    <div>
                        <div className="font-medium">In crisis right now?</div>
                        <p className="text-sm text-muted-foreground mt-1">
                            Call <strong className="text-foreground">988</strong> (US) · <strong className="text-foreground">116 123</strong> (UK Samaritans) · <strong className="text-foreground">13 11 14</strong> (AU Lifeline) — or open the in-app <em>Need help now?</em> link for full local listings.
                        </p>
                    </div>
                </div>
            </div>

            <h2 className="font-display text-2xl font-medium tracking-tight mt-12 mb-4">Frequently asked</h2>
            <div className="space-y-3">
                <Faq q="What is Anchor?">
                    <p>Anchor is a private self-tracking app for people in alcohol recovery. You log your sobriety streak, daily mood, diet (protein/salt/water), blood markers, medications, and weekly goals — and the app turns that into trends, AI-generated weekly reflections, and clinician-ready reports.</p>
                </Faq>
                <Faq q="Is Anchor a substitute for therapy or medical care?">
                    <p><strong>No.</strong> Anchor is a tracking tool. It supports your recovery — it doesn't replace doctors, therapists, sponsors, or emergency services. If you're in crisis, please use the helplines above.</p>
                </Faq>
                <Faq q="Where is my data stored, and who can see it?">
                    <p>Your data is stored in MongoDB Atlas (cloud), tied to your account. <strong>Only you can see it.</strong> The only exception is when you explicitly create a share link for a sponsor (read-only, expires when you say) or email a PDF report to someone. Read our full <Link to="/privacy" className="text-primary underline">Privacy Policy</Link> for details.</p>
                </Faq>
                <Faq q="How does the food label scanner work?">
                    <p>You upload a photo of a nutrition label and AI (OpenAI GPT-5.2 vision) extracts the values — protein, salt, sodium, calories. You confirm or edit the numbers, then add it to today's diet. The photo is not retained after extraction.</p>
                </Faq>
                <Faq q="How does the blood test extractor work?">
                    <p>Same idea — upload a photo of a lab report and AI extracts markers (ALT, AST, GGT, bilirubin, MCV, and others). <strong>Tip:</strong> crop or cover any identifying info (your name, NHS/Medicare number, DOB) before uploading if you'd rather not share that with the AI provider.</p>
                </Faq>
                <Faq q="Why do the diet targets say salt ≤ 2g and water ≤ 1.5L?">
                    <p>These targets follow specific recovery-focused dietary guidance — high protein (≥140g/day) to support liver repair and muscle recovery, low salt to reduce strain on a healing liver, and a water cap to avoid electrolyte imbalance in people with damaged liver function. Always follow your own doctor's recommendation if it differs.</p>
                </Faq>
                <Faq q="How do I email a report to my doctor?">
                    <p>Open <strong>Reports</strong> in the side menu → choose period (week/month) and scope (clinical/full/personal) → fill in your doctor's email and an optional note → click <em>Send report</em>. They'll get a PDF attachment by email; you can reply to that email directly.</p>
                </Faq>
                <Faq q="How do I share my progress with a sponsor?">
                    <p>Open <strong>Share</strong> in the side menu → choose <em>Summary</em> (no diary entries) or <em>Full</em> (includes recent diary) and an expiry (1–30 days) → click <em>Create link</em> → copy and send the link to your sponsor. They can view it in any browser without signing up. You can revoke the link at any time from the same page.</p>
                </Faq>
                <Faq q="How do I change my sobriety start date?">
                    <p>Open <strong>Profile</strong> in the side menu → update the <em>Sobriety start date</em> field → click <em>Save changes</em>. Your streak counter recalculates immediately.</p>
                </Faq>
                <Faq q="Can I delete my account and all my data?">
                    <p>Yes. Email <a className="text-primary underline" href="mailto:support@anchorhelp.com.au">support@anchorhelp.com.au</a> from your registered address and ask for account deletion. We'll remove all your data within 30 days and confirm by email.</p>
                </Faq>
                <Faq q="Is Anchor free?">
                    <p>Yes — Anchor is free to use. We may add a Pro tier in the future, but everything you see today will remain free.</p>
                </Faq>
                <Faq q="What if I relapse?">
                    <p>A relapse isn't a failure — it's a step on the recovery journey. You can reset your sobriety start date in Profile any time. The app will not judge you, lecture you, or send you a guilt-trip email. It just quietly starts counting again.</p>
                </Faq>
            </div>

            {/* Contact card */}
            <div className="tactile-card p-6 sm:p-8 mt-12 text-center" data-testid="support-contact">
                <Mail className="w-6 h-6 text-primary mx-auto" strokeWidth={1.5} />
                <h2 className="font-display text-2xl font-medium tracking-tight mt-3">Still stuck?</h2>
                <p className="text-sm text-muted-foreground mt-2">We aim to reply within one business day.</p>
                <a href="mailto:support@anchorhelp.com.au" className="anchor-btn-primary inline-block mt-5 no-underline">
                    Email support
                </a>
            </div>

            <div className="text-xs text-muted-foreground mt-12 pt-6 border-t border-border flex flex-wrap gap-6">
                <Link to="/" className="hover:text-primary">Home</Link>
                <Link to="/privacy" className="hover:text-primary">Privacy Policy</Link>
                <a href="mailto:support@anchorhelp.com.au" className="hover:text-primary">Contact</a>
            </div>
        </div>
    </div>
);

export default Support;
