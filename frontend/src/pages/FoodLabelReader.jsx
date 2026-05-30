import React, { useState } from "react";
import { api, imageFileToJpegBase64, todayStr } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { toast } from "sonner";
import { Camera, Upload, Loader2, Check } from "lucide-react";

const FOOD_PLACEHOLDER = "https://images.unsplash.com/photo-1759191639442-be1b99d1eb57?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwZm9vZCUyMGluZ3JlZGllbnRzJTIwd2FybSUyMGxpZ2h0fGVufDB8fHx8MTc3ODY0NzMzMnww&ixlib=rb-4.1.0&q=85";

const FoodLabelReader = () => {
    const [preview, setPreview] = useState(null);
    const [extracting, setExtracting] = useState(false);
    const [result, setResult] = useState(null);
    const [logging, setLogging] = useState(false);

    const onFile = async (file) => {
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => setPreview(reader.result);
        reader.readAsDataURL(file);

        setExtracting(true);
        setResult(null);
        try {
            const b64 = await imageFileToJpegBase64(file);
            const { data } = await api.post("/food-label/analyze", { image_base64: b64 });
            setResult(data);
            const hasData = data && (data.name || data.protein_g || data.calories || data.salt_g);
            if (hasData) {
                toast.success("Label analyzed — review and log");
            } else {
                toast.message("We couldn't read that label clearly", {
                    description: "Try a closer, glare-free photo of the nutrition panel — or edit the fields manually before logging.",
                });
            }
        } catch (err) {
            toast.error(err?.response?.data?.detail || err?.message || "Could not analyze");
        } finally {
            setExtracting(false);
        }
    };

    const updateField = (k, v) => setResult((p) => ({ ...p, [k]: v }));

    const logIt = async () => {
        if (!result) return;
        setLogging(true);
        try {
            await api.post("/meals", {
                date: todayStr(),
                name: result.name || "Scanned item",
                protein_g: parseFloat(result.protein_g) || 0,
                salt_g: parseFloat(result.salt_g) || 0,
                water_ml: 0,
                calories: parseFloat(result.calories) || 0,
                notes: result.serving_size ? `Serving: ${result.serving_size}` : "",
            });
            toast.success("Added to today's diet");
            setResult(null);
            setPreview(null);
        } catch (err) {
            toast.error("Could not log");
        } finally {
            setLogging(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto fade-up" data-testid="food-label-root">
            <div className="label-eyebrow">Food label reader</div>
            <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tight mt-1">Scan a label.</h1>
            <p className="text-muted-foreground mt-3">Snap a photo of the nutrition panel — we'll pull the numbers.</p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-10">
                <label
                    htmlFor="food-upload"
                    className="tactile-card border-dashed border-2 border-primary/40 hover:border-primary cursor-pointer p-8 min-h-[320px] flex flex-col items-center justify-center text-center transition-colors"
                    data-testid="food-upload-dropzone"
                >
                    {preview ? (
                        <img src={preview} alt="label preview" className="max-h-[280px] rounded-2xl object-contain" />
                    ) : (
                        <>
                            <img src={FOOD_PLACEHOLDER} alt="" className="w-32 h-32 object-cover rounded-2xl mb-4 opacity-70" />
                            <Camera className="w-6 h-6 text-primary mb-2" strokeWidth={1.5} />
                            <div className="font-medium">Upload nutrition label</div>
                            <div className="text-xs text-muted-foreground mt-1">JPG, PNG, or WEBP</div>
                        </>
                    )}
                    <input
                        id="food-upload"
                        data-testid="food-upload-input"
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => onFile(e.target.files?.[0])}
                    />
                </label>

                <div className="tactile-card p-6 sm:p-8" data-testid="food-result-card">
                    {extracting && (
                        <div className="flex items-center gap-3 text-muted-foreground">
                            <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} /> Reading the label…
                        </div>
                    )}
                    {!extracting && !result && (
                        <div className="text-sm text-muted-foreground">
                            Upload an image and we'll extract protein, salt, calories and more — ready to log.
                        </div>
                    )}
                    {result && (
                        <div className="space-y-4">
                            <div>
                                <label className="label-eyebrow">Item</label>
                                <Input data-testid="food-result-name" value={result.name || ""} onChange={(e) => updateField("name", e.target.value)} className="mt-1" />
                            </div>
                            <div>
                                <label className="label-eyebrow">Serving</label>
                                <Input data-testid="food-result-serving" value={result.serving_size || ""} onChange={(e) => updateField("serving_size", e.target.value)} className="mt-1" />
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="label-eyebrow">Protein (g)</label>
                                    <Input data-testid="food-result-protein" type="number" value={result.protein_g ?? ""} onChange={(e) => updateField("protein_g", e.target.value)} className="mt-1" />
                                </div>
                                <div>
                                    <label className="label-eyebrow">Salt (g)</label>
                                    <Input data-testid="food-result-salt" type="number" step="0.01" value={result.salt_g ?? ""} onChange={(e) => updateField("salt_g", e.target.value)} className="mt-1" />
                                </div>
                                <div>
                                    <label className="label-eyebrow">Sodium (mg)</label>
                                    <Input type="number" value={result.sodium_mg ?? ""} onChange={(e) => updateField("sodium_mg", e.target.value)} className="mt-1" />
                                </div>
                                <div>
                                    <label className="label-eyebrow">Calories</label>
                                    <Input data-testid="food-result-calories" type="number" value={result.calories ?? ""} onChange={(e) => updateField("calories", e.target.value)} className="mt-1" />
                                </div>
                            </div>
                            <Button onClick={logIt} disabled={logging} data-testid="food-log-btn" className="rounded-full px-6 w-full">
                                <Check className="w-4 h-4 mr-1" strokeWidth={1.5} />
                                {logging ? "Adding…" : "Add to today's diet"}
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FoodLabelReader;
