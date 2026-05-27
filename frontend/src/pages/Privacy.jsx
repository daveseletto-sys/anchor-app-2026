import React from "react";
import { Link } from "react-router-dom";
import { Anchor } from "lucide-react";

const H2 = ({ children }) => (
    <h2 className="font-display text-2xl font-medium tracking-tight mt-10 mb-3">{children}</h2>
);
const P = ({ children }) => (
    <p className="text-base leading-[1.75] text-foreground/90 mb-4">{children}</p>
);

const Privacy = () => (
    <div className="min-h-screen bg-background p-6 sm:p-12 fade-up" data-testid="privacy-root">
        <div className="max-w-3xl mx-auto">
            <Link to="/" className="flex items-center gap-2 mb-8">
                <Anchor className="w-5 h-5 text-primary" strokeWidth={1.5} />
                <span className="font-display font-semibold tracking-tight">Anchor</span>
            </Link>

            <div className="label-eyebrow">Privacy Policy</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Your data is yours.</h1>
            <p className="text-muted-foreground mt-3">Last updated: February 2026</p>

            <P>
                Anchor ("we", "us", "the app") is a private companion for people managing alcohol use disorder. We take your privacy seriously
                — recovery is a deeply personal journey, and the data you log here is sensitive health information. This policy explains exactly
                what we collect, why, how it's protected, and what your rights are.
            </P>

            <H2>1. What we collect</H2>
            <P><strong>Account data</strong> — email address, name, hashed password (we never store your plain password).</P>
            <P><strong>Recovery data you choose to log</strong> — sobriety start date, diary entries (date, 1–10 rating, mood tags, free-text notes), meals (protein, salt, water, calories, name), blood test results (markers, values, units, dates), medications (name, dose, schedule, adherence), weekly goals, height, weight, and region.</P>
            <P><strong>Images you upload</strong> — photos of food labels and blood test reports. These are processed for nutrition / marker extraction (see Section 3) and not retained after extraction completes unless you save the result.</P>
            <P><strong>Technical data</strong> — IP address (transient, for security), session tokens (stored in your device's local storage), and basic server logs.</P>
            <P>We do <strong>not</strong> collect: precise location, contacts, advertising IDs, browsing history outside the app, social-media profiles, or biometric data.</P>

            <H2>2. Why we collect it</H2>
            <P>To deliver the features you use: track your sobriety, generate weekly AI reflections, render charts and trends, export PDF reports, send digest emails, share read-only links with sponsors (only when you create them), and run privacy-protected community averages (see Section 4).</P>

            <H2>3. AI processing</H2>
            <P>Two app features send data to third-party AI services:</P>
            <P>• <strong>Food label reader</strong> — your photo is sent to OpenAI (GPT-5.2 vision) via the Emergent Integrations gateway for nutrition extraction. The image is not used to train models.</P>
            <P>• <strong>Blood test extractor</strong> — your photo is sent to OpenAI (GPT-5.2 vision) for marker extraction. The image is not used to train models. <strong>Do not upload images that contain your full legal name, address, NHS/Medicare number, or other identifying information you don't want to share with a third party.</strong> Crop the image to just the lab results section if you're concerned.</P>
            <P>• <strong>Weekly AI reflection</strong> — your last 7 days of diary, diet, medication adherence, and goal completion (NOT raw identifiers, NOT the diary's free-text notes) are summarised by Anthropic Claude Sonnet 4.5. The reflection text is stored in our database so you can revisit it.</P>

            <H2>4. Community averages — anonymous</H2>
            <P>If you view the Milestones page, you'll see "Anonymous community averages" — these are computed across all Anchor users for the last 30 days. We only show them when at least 5 users are in the data (k-anonymity threshold) and the result contains <strong>no names, no rankings, and no identifying information</strong> — only aggregated averages.</P>

            <H2>5. Sharing</H2>
            <P>You — and only you — can create read-only share links with a sponsor, partner, or coach. Each link has an expiry date you choose (1–90 days) and can be revoked at any time. We do not share your data with any third party for marketing.</P>

            <H2>6. Where your data lives</H2>
            <P>Your data is stored in MongoDB Atlas (managed cloud database). Outbound emails (digests, reports to your doctor) are sent via Resend. We do not sell, rent, or share your data with advertisers.</P>

            <H2>7. Retention &amp; deletion</H2>
            <P>Your data is kept as long as your account is active. You can delete your account at any time from within the app — open <strong>Profile → Delete account</strong>, type DELETE to confirm, and we will immediately and permanently remove your account along with every piece of data linked to it (diary entries, meals, blood tests, medications, goals, AI reflections, and share links). No 30-day waiting period; deletion is irreversible. You can also email <a className="text-primary underline" href="mailto:support@anchorhelp.com.au">support@anchorhelp.com.au</a> if you'd prefer assisted deletion. To take a copy of your data with you, generate a "Full" PDF report from the Reports page before deleting.</P>

            <H2>8. Children</H2>
            <P>Anchor is intended for adults (17+). It is not designed for or directed at children, and we do not knowingly collect data from anyone under 17. If you believe a minor has created an account, please contact us and we will delete the account immediately.</P>

            <H2>9. Security</H2>
            <P>Passwords are hashed with bcrypt. All traffic between your device and our servers uses HTTPS. We follow industry-standard practices for access control and review our systems regularly. No system is perfectly secure — if a breach occurs, we will notify affected users within 72 hours.</P>

            <H2>10. Your rights</H2>
            <P>Depending on where you live (GDPR, CCPA, Australian Privacy Principles), you have the right to access, correct, export, restrict, or delete your data. Email <a className="text-primary underline" href="mailto:support@anchorhelp.com.au">support@anchorhelp.com.au</a> with your request.</P>

            <H2>11. Crisis disclaimer</H2>
            <P>Anchor is a self-tracking tool — <strong>it is not a substitute for clinical care, therapy, or emergency services</strong>. If you or someone you know is in immediate danger, call 911 (US), 999 (UK), 000 (Australia), or your local emergency number. The app's Crisis page lists region-specific helplines.</P>

            <H2>12. Changes to this policy</H2>
            <P>We'll update this page with the date at the top when anything changes. Material changes will be announced via in-app notice and an email to your registered address.</P>

            <H2>Contact</H2>
            <P>
                Anchor Recovery<br />
                <a className="text-primary underline" href="mailto:support@anchorhelp.com.au">support@anchorhelp.com.au</a><br />
                <a className="text-primary underline" href="https://anchorhelp.com.au">anchorhelp.com.au</a>
            </P>

            <div className="text-xs text-muted-foreground mt-12 pt-6 border-t border-border flex flex-wrap gap-6">
                <Link to="/" className="hover:text-primary">Home</Link>
                <Link to="/support" className="hover:text-primary">Support</Link>
                <a href="mailto:support@anchorhelp.com.au" className="hover:text-primary">Contact</a>
            </div>
        </div>
    </div>
);

export default Privacy;
