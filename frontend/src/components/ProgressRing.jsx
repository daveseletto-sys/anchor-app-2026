import React from "react";

const clamp = (v) => Math.max(0, Math.min(1, v));

/**
 * ProgressRing - SVG circular progress
 * variant: "fill" (good when full) or "limit" (good when low; turns terracotta past 100%)
 */
const ProgressRing = ({
    value = 0,
    target = 100,
    label = "",
    unit = "",
    color = "primary",
    variant = "fill",
    size = 140,
    testId,
}) => {
    const stroke = 10;
    const radius = (size - stroke) / 2;
    const circumference = 2 * Math.PI * radius;
    const ratio = clamp(value / Math.max(target, 0.0001));
    const offset = circumference - ratio * circumference;

    const colorMap = {
        primary: "stroke-[hsl(136_18%_35%)]",
        terracotta: "stroke-[hsl(13_54%_55%)]",
        sky: "stroke-[hsl(200_18%_51%)]",
        ochre: "stroke-[hsl(39_60%_56%)]",
    };
    const over = variant === "limit" && value > target;
    const strokeClass = over ? "stroke-[hsl(13_54%_55%)]" : colorMap[color] || colorMap.primary;

    return (
        <div className="flex flex-col items-center" data-testid={testId}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    className="stroke-[hsl(42_20%_88%)]"
                    strokeWidth={stroke}
                />
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    className={`${strokeClass} transition-all duration-1000 ease-out`}
                    strokeWidth={stroke}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                />
            </svg>
            <div className="-mt-[88px] text-center pointer-events-none">
                <div className="font-display text-2xl font-semibold tracking-tight">
                    {Number(value).toFixed(value < 10 ? 1 : 0)}
                    <span className="text-sm text-muted-foreground font-normal ml-1">{unit}</span>
                </div>
                <div className="label-eyebrow mt-1">{label}</div>
                <div className="text-xs text-muted-foreground mt-1">
                    {variant === "limit" ? "max" : "goal"} {target}
                    {unit}
                </div>
            </div>
            <div className="h-[60px]" />
        </div>
    );
};

export default ProgressRing;
