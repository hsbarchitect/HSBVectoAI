"use client";

import { motion } from "framer-motion";
import { Zap, PenTool, Layers, Cpu, ChevronRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

function Navbar() {
  return (
    <header className="fixed top-0 inset-x-0 z-50 glass-panel border-b-0 border-white/5 h-16 sm:h-20 flex items-center px-6 md:px-12">
      <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shadow-lg shadow-brand-500/20">
          <Zap className="w-5 h-5 text-white fill-white" />
        </div>
        <span className="text-white">HSBVecto<span className="text-brand-500">AI</span></span>
      </div>
      <div className="ml-auto hidden md:flex items-center gap-8 text-sm font-medium text-white/70">
        <Link href="#features" className="hover:text-white transition-colors">Features</Link>
        <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
        <Link href="/docs" className="hover:text-white transition-colors">Documentation</Link>
      </div>
      <div className="ml-auto md:ml-8 flex items-center gap-4">
        <Link href="/login" className="text-sm font-medium hover:text-white transition-colors hidden sm:block">Log In</Link>
        <Link href="/login" className="px-5 py-2.5 rounded-full bg-white text-surface-950 text-sm font-bold hover:bg-brand-50 transition-colors shadow-lg shadow-white/10">
          Get Started
        </Link>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="relative pt-40 pb-20 md:pt-52 md:pb-32 px-6 flex flex-col items-center text-center overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-500/20 rounded-full blur-[120px] pointer-events-none" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel border-white/10 text-sm font-medium text-brand-400 mb-8"
      >
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
        </span>
        VectoAI Desktop Beta is now live
      </motion.div>

      <motion.h1 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="text-5xl md:text-7xl font-bold tracking-tight max-w-4xl leading-[1.1]"
      >
        Design <span className="text-gradient">Smarter</span>, Not Harder in <span className="text-gradient-brand">CorelDRAW</span>
      </motion.h1>

      <motion.p 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mt-8 text-lg md:text-xl text-white/60 max-w-2xl font-light"
      >
        HSBVectoAI is your intelligent copilot for CorelDRAW. Automate tedious tasks, generate vectors instantly, and control your workspace with natural language.
      </motion.p>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="mt-10 flex flex-col sm:flex-row items-center gap-4"
      >
        <Link href="/download" className="px-8 py-4 rounded-full bg-gradient-to-r from-brand-400 to-brand-600 text-white font-bold text-lg hover:shadow-lg hover:shadow-brand-500/25 transition-all flex items-center gap-2 group">
          Download Desktop App
          <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </Link>
        <Link href="#demo" className="px-8 py-4 rounded-full glass-panel hover:bg-white/5 transition-all font-semibold">
          Watch Demo
        </Link>
      </motion.div>

      {/* Hero Image / Mockup */}
      <motion.div 
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.4 }}
        className="mt-20 w-full max-w-5xl aspect-video rounded-2xl glass-panel border-white/10 p-2 shadow-2xl relative"
      >
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-surface-950/80 rounded-2xl z-10" />
        <div className="w-full h-full rounded-xl bg-surface-900 border border-white/5 overflow-hidden flex items-center justify-center relative">
          <div className="absolute top-4 left-4 flex gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>
          <div className="text-white/20 font-medium text-lg flex items-center gap-3">
            <Cpu className="w-8 h-8" />
            AI Interface Mockup
          </div>
        </div>
      </motion.div>
    </section>
  );
}

const FEATURES = [
  {
    icon: <PenTool className="w-6 h-6 text-brand-400" />,
    title: "Instant Vector Generation",
    description: "Describe what you want, and watch HSBVectoAI draw it directly onto your CorelDRAW canvas in real-time."
  },
  {
    icon: <Layers className="w-6 h-6 text-brand-400" />,
    title: "Layer Management",
    description: "Organize, rename, and group thousands of layers instantly using AI logic instead of manual clicking."
  },
  {
    icon: <Cpu className="w-6 h-6 text-brand-400" />,
    title: "Context-Aware AI",
    description: "The AI sees your currently selected objects and understands your document dimensions and color profiles."
  }
];

function FeatureSection() {
  return (
    <section id="features" className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-bold">Supercharge your workflow</h2>
        <p className="mt-4 text-white/60 max-w-2xl mx-auto">Everything you need to create faster and eliminate repetitive design tasks.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {FEATURES.map((feature, idx) => (
          <div key={idx} className="glass-panel p-8 rounded-2xl hover:bg-white/5 transition-colors border-white/5">
            <div className="w-12 h-12 rounded-xl bg-brand-500/10 flex items-center justify-center mb-6">
              {feature.icon}
            </div>
            <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
            <p className="text-white/60 leading-relaxed">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className="py-24 px-6 md:px-12 max-w-5xl mx-auto text-center">
      <div className="glass-panel p-12 md:p-20 rounded-3xl relative overflow-hidden border-brand-500/20">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-brand-500/10 blur-[100px] pointer-events-none" />
        <h2 className="text-3xl md:text-5xl font-bold mb-6">Ready to transform how you design?</h2>
        <p className="text-white/60 mb-10 max-w-xl mx-auto text-lg">Join thousands of designers who are saving hours every day with HSBVectoAI.</p>
        <Link href="/download" className="px-8 py-4 rounded-full bg-white text-surface-950 font-bold text-lg hover:bg-brand-50 transition-colors shadow-xl shadow-white/10 inline-flex">
          Get Started for Free
        </Link>
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-white/60">
          <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-brand-500" /> No credit card required</div>
          <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-brand-500" /> 14-day free trial on Pro</div>
          <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-brand-500" /> Works with CorelDRAW 2021+</div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-white/10 py-12 px-6 md:px-12 mt-12">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2 font-bold text-lg">
          <Zap className="w-5 h-5 text-brand-500 fill-brand-500" />
          HSBVectoAI
        </div>
        <div className="text-white/40 text-sm">
          © {new Date().getFullYear()} HSB Architect. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default function Home() {
  return (
    <main className="flex-1">
      <Navbar />
      <Hero />
      <FeatureSection />
      <CTASection />
      <Footer />
    </main>
  );
}
