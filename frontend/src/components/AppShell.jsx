import React from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { Anchor, Home, BookOpen, UtensilsCrossed, Camera, Activity, Target, BookText, LogOut, Pill, UserCircle, LifeBuoy, FileDown } from "lucide-react";
import { useAuth } from "../lib/auth";

const NAV = [
    { to: "/app", label: "Dashboard", icon: Home, end: true },
    { to: "/app/diary", label: "Daily Diary", icon: BookOpen },
    { to: "/app/diet", label: "Diet Tracker", icon: UtensilsCrossed },
    { to: "/app/food-label", label: "Food Label", icon: Camera },
    { to: "/app/blood", label: "Blood Tests", icon: Activity },
    { to: "/app/meds", label: "Medications", icon: Pill },
    { to: "/app/goals", label: "Weekly Goals", icon: Target },
    { to: "/app/reports", label: "Reports", icon: FileDown },
    { to: "/app/glossary", label: "Glossary", icon: BookText },
    { to: "/app/profile", label: "Profile", icon: UserCircle },
];

const AppShell = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/");
    };

    return (
        <div className="min-h-screen bg-background flex">
            {/* Sidebar */}
            <aside className="hidden md:flex md:w-64 flex-col border-r border-border bg-card/40 p-6 sticky top-0 h-screen">
                <Link to="/app" className="flex items-center gap-2 mb-10" data-testid="sidebar-logo">
                    <Anchor className="w-6 h-6 text-primary" strokeWidth={1.5} />
                    <span className="font-display font-semibold text-xl tracking-tight">Anchor</span>
                </Link>
                <nav className="flex flex-col gap-1 flex-1">
                    {NAV.map((item) => {
                        const Icon = item.icon;
                        return (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                end={item.end}
                                data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, "-")}`}
                                className={({ isActive }) =>
                                    `flex items-center gap-3 px-4 py-3 rounded-2xl text-sm transition-colors ${
                                        isActive
                                            ? "bg-primary/10 text-primary font-medium"
                                            : "text-muted-foreground hover:bg-secondary"
                                    }`
                                }
                            >
                                <Icon className="w-4 h-4" strokeWidth={1.5} />
                                {item.label}
                            </NavLink>
                        );
                    })}
                </nav>
                <div className="border-t border-border pt-4 mt-4">
                    <NavLink
                        to="/app/crisis"
                        data-testid="nav-crisis"
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-3 rounded-2xl text-sm transition-colors mb-2 ${
                                isActive
                                    ? "bg-accent/15 text-accent font-medium"
                                    : "text-accent hover:bg-accent/10"
                            }`
                        }
                    >
                        <LifeBuoy className="w-4 h-4" strokeWidth={1.5} />
                        Need help now?
                    </NavLink>
                    <div className="px-2 mb-3">
                        <div className="text-xs text-muted-foreground">Signed in as</div>
                        <div className="text-sm font-medium truncate" data-testid="sidebar-user">{user?.name || user?.email}</div>
                    </div>
                    <button
                        onClick={handleLogout}
                        data-testid="logout-btn"
                        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground px-2 py-2 transition-colors"
                    >
                        <LogOut className="w-4 h-4" strokeWidth={1.5} />
                        Sign out
                    </button>
                </div>
            </aside>

            {/* Mobile top bar */}
            <div className="md:hidden fixed top-0 inset-x-0 z-30 bg-background border-b border-border">
                <div className="flex items-center justify-between p-4">
                    <Link to="/app" className="flex items-center gap-2">
                        <Anchor className="w-5 h-5 text-primary" strokeWidth={1.5} />
                        <span className="font-display font-semibold tracking-tight">Anchor</span>
                    </Link>
                    <button onClick={handleLogout} data-testid="logout-btn-mobile" className="text-sm text-muted-foreground">
                        Sign out
                    </button>
                </div>
                <div className="flex overflow-x-auto gap-1 px-3 pb-3 no-scrollbar">
                    {NAV.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.end}
                            className={({ isActive }) =>
                                `whitespace-nowrap text-xs px-3 py-2 rounded-full ${
                                    isActive ? "bg-primary text-primary-foreground" : "bg-secondary text-muted-foreground"
                                }`
                            }
                        >
                            {item.label}
                        </NavLink>
                    ))}
                </div>
            </div>

            <main className="flex-1 md:p-10 p-4 pt-28 md:pt-10">
                <Outlet />
            </main>
        </div>
    );
};

export default AppShell;
