"use client";

import { motion } from "framer-motion";
import { LogOut, User, Zap, Download, CreditCard, Activity, Settings } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();

  const handleLogout = () => {
    // Simulate logout
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-surface-950 flex flex-col md:flex-row">
      {/* Sidebar */}
      <aside className="w-full md:w-64 border-b md:border-b-0 md:border-r border-white/10 p-6 flex flex-col glass-panel shrink-0">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight mb-10">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Zap className="w-5 h-5 text-white fill-white" />
          </div>
          <span className="text-white">HSBVecto<span className="text-brand-500">AI</span></span>
        </Link>
        
        <nav className="flex-1 space-y-2">
          <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/10 text-white font-medium transition-colors">
            <Activity className="w-5 h-5" /> Overview
          </Link>
          <Link href="/dashboard/billing" className="flex items-center gap-3 px-4 py-3 rounded-xl text-white/60 hover:text-white hover:bg-white/5 font-medium transition-colors">
            <CreditCard className="w-5 h-5" /> Billing & Plan
          </Link>
          <Link href="/dashboard/settings" className="flex items-center gap-3 px-4 py-3 rounded-xl text-white/60 hover:text-white hover:bg-white/5 font-medium transition-colors">
            <Settings className="w-5 h-5" /> Settings
          </Link>
        </nav>

        <div className="mt-auto pt-8 border-t border-white/10">
          <div className="flex items-center gap-3 px-4 py-3 mb-2">
            <div className="w-8 h-8 rounded-full bg-surface-800 flex items-center justify-center">
              <User className="w-4 h-4 text-white/60" />
            </div>
            <div className="text-sm">
              <div className="font-medium">Selim Batı</div>
              <div className="text-white/40 text-xs">selim@hsbvectoai.com</div>
            </div>
          </div>
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-red-400/10 font-medium transition-colors">
            <LogOut className="w-5 h-5" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 md:p-12 overflow-y-auto">
        <header className="mb-10">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-white/60">Manage your subscription, usage, and devices.</p>
        </header>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          {/* Plan Card */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel p-6 rounded-2xl border-white/10"
          >
            <div className="flex items-start justify-between mb-4">
              <h3 className="font-medium text-white/60">Current Plan</h3>
              <div className="px-2.5 py-1 rounded-md bg-brand-500/20 text-brand-400 text-xs font-bold uppercase tracking-wider">
                PRO TIER
              </div>
            </div>
            <div className="text-3xl font-bold mb-1">Pro Plan</div>
            <p className="text-white/40 text-sm mb-6">Renews on August 15, 2026</p>
            <Link href="/pricing" className="text-brand-400 text-sm font-medium hover:text-brand-300">Manage Billing &rarr;</Link>
          </motion.div>

          {/* Usage Card */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-panel p-6 rounded-2xl border-white/10"
          >
            <div className="flex items-start justify-between mb-4">
              <h3 className="font-medium text-white/60">AI Operations Used</h3>
              <Activity className="w-5 h-5 text-brand-400" />
            </div>
            <div className="text-3xl font-bold mb-2">142 <span className="text-lg text-white/40 font-normal">/ Unlimited</span></div>
            <div className="w-full h-2 bg-surface-800 rounded-full overflow-hidden mb-2">
              <div className="h-full bg-gradient-to-r from-brand-400 to-brand-600 w-1/4 rounded-full" />
            </div>
            <p className="text-white/40 text-xs">Based on current billing cycle</p>
          </motion.div>

          {/* Devices Card */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-panel p-6 rounded-2xl border-white/10"
          >
            <div className="flex items-start justify-between mb-4">
              <h3 className="font-medium text-white/60">Active Devices</h3>
              <div className="text-white/40 text-sm">1 / 3</div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-900 border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-sm font-medium">DESKTOP-75PFM1T</span>
                </div>
                <button className="text-xs text-red-400 hover:text-red-300">Revoke</button>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Download Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="relative overflow-hidden rounded-3xl glass-panel p-8 md:p-12 border-brand-500/20"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-[80px] pointer-events-none" />
          
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div>
              <h2 className="text-2xl font-bold mb-3">Download the Desktop App</h2>
              <p className="text-white/60 max-w-xl">
                Install HSBVectoAI on your Windows machine to start automating CorelDRAW. 
                Compatible with CorelDRAW 2021 and newer versions.
              </p>
            </div>
            <button className="shrink-0 px-8 py-4 rounded-xl bg-gradient-to-r from-brand-400 to-brand-600 text-white font-bold hover:shadow-lg hover:shadow-brand-500/25 transition-all flex items-center gap-3">
              <Download className="w-5 h-5" />
              Download for Windows
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
