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
