import axios from "axios";

export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("anchor_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

export const todayStr = () => new Date().toISOString().slice(0, 10);

export const mondayOf = (d = new Date()) => {
    const dt = new Date(d);
    const day = (dt.getDay() + 6) % 7; // 0 = Monday
    dt.setDate(dt.getDate() - day);
    return dt.toISOString().slice(0, 10);
};

export const fileToBase64 = (file) =>
    new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const result = reader.result || "";
            const idx = String(result).indexOf(",");
            resolve(idx >= 0 ? String(result).slice(idx + 1) : String(result));
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });

/**
 * Convert any image file (JPG/PNG/WEBP/HEIC/HEIF) to a JPEG base64 string.
 * Decodes via the browser (iOS Safari/WKWebView handles HEIC natively),
 * draws to canvas, downscales so the longest side <= maxSide, re-encodes as JPEG.
 * Returns a base64 string (no data: prefix).
 */
export const imageFileToJpegBase64 = (file, { maxSide = 1600, quality = 0.85 } = {}) =>
    new Promise((resolve, reject) => {
        if (!file) {
            reject(new Error("No file"));
            return;
        }
        const dataReader = new FileReader();
        dataReader.onerror = () => reject(new Error("Could not read file"));
        dataReader.onload = () => {
            const img = new Image();
            img.onerror = () => {
                // Fallback: send the original bytes as base64 (some HEICs may not decode in non-Safari browsers)
                const idx = String(dataReader.result || "").indexOf(",");
                if (idx >= 0) resolve(String(dataReader.result).slice(idx + 1));
                else reject(new Error("Image could not be decoded. Try a JPG or PNG."));
            };
            img.onload = () => {
                try {
                    const w0 = img.naturalWidth || img.width;
                    const h0 = img.naturalHeight || img.height;
                    if (!w0 || !h0) {
                        reject(new Error("Image has no dimensions"));
                        return;
                    }
                    const scale = Math.min(1, maxSide / Math.max(w0, h0));
                    const w = Math.round(w0 * scale);
                    const h = Math.round(h0 * scale);
                    const canvas = document.createElement("canvas");
                    canvas.width = w;
                    canvas.height = h;
                    const ctx = canvas.getContext("2d");
                    // White background in case source is transparent (improves OCR contrast)
                    ctx.fillStyle = "#ffffff";
                    ctx.fillRect(0, 0, w, h);
                    ctx.drawImage(img, 0, 0, w, h);
                    const dataUrl = canvas.toDataURL("image/jpeg", quality);
                    const idx = dataUrl.indexOf(",");
                    resolve(idx >= 0 ? dataUrl.slice(idx + 1) : dataUrl);
                } catch (e) {
                    reject(e);
                }
            };
            img.src = dataReader.result;
        };
        dataReader.readAsDataURL(file);
    });
