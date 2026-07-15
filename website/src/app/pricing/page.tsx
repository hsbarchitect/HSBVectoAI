"use client";

import { motion } from "framer-motion";
import { Check, ChevronLeft, Zap } from "lucide-react";
import Link from "next/link";

const PLANS = [
  {
    name: "Starter",
    price: "9",
    currency: "$",
    description: "Perfect for freelancers and occasional CorelDRAW users.",
    features: [
      "500 AI operations per month",
      "Standard vector generation",
      "1 Device license",
      "Email support"
    ],
    popular: false,
    cta: "Start Free Trial"
  },
  {
    name: "Pro",
    price: "18",
    currency: "$",
    description: "For professionals who design daily in CorelDRAW.",
    features: [
      "Unlimited AI operations",
      "Priority API processing",
      "3 Device licenses",
      "Advanced layer management",
      "Priority support"
    ],
    popular: true,
    cta: "Get Pro"
  },
  {
    name: "Studio",
    price: "35",
    currency: "$",
    description: "For design teams and agencies.",
    features: [
      "Everything in Pro",
      "10 Device licenses",
      "Team billing",
      "Custom model tuning",
      "24/7 dedicated support"
    ],
    popular: false,
    cta: "Contact Sales"
  }
];

export default function PricingPage() {
  return (
    <main className="min-h-screen pt-32 pb-24 px-6 md:px-12 flex flex-col items-center">
      <Link href="/" className="absolute top-8 left-6 md:left-12 flex items-center gap-2 text-white/60 hover:text-white transition-colors">
        <ChevronLeft className="w-5 h-5" />
        Back to Home
      </Link>

      <div className="text-center mb-16 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-brand-500/20 rounded-full blur-[100px] pointer-events-none" />
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4 relative z-10">Simple, transparent pricing</h1>
        <p className="text-lg text-white/60 max-w-xl mx-auto relative z-10">Choose the plan that best fits your design workflow. Upgrade or downgrade at any time.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto w-full relative z-10">
        {PLANS.map((plan, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1, duration: 0.5 }}
            className={`glass-panel p-8 rounded-3xl relative flex flex-col ${plan.popular ? 'border-brand-500 shadow-2xl shadow-brand-500/10 scale-105 z-10' : 'border-white/10'}`}
          >
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-brand-400 to-brand-600 text-white text-sm font-bold shadow-lg">
                Most Popular
              </div>
            )}
            
            <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
            <p className="text-white/60 text-sm mb-6 h-10">{plan.description}</p>
            
            <div className="mb-8">
              <span className="text-5xl font-bold">{plan.currency}{plan.price}</span>
              <span className="text-white/40">/month</span>
            </div>
            
            <ul className="space-y-4 mb-8 flex-1">
              {plan.features.map((feature, fIdx) => (
                <li key={fIdx} className="flex items-start gap-3">
                  <div className="mt-1 w-5 h-5 rounded-full bg-brand-500/20 flex items-center justify-center shrink-0">
                    <Check className="w-3 h-3 text-brand-400" />
                  </div>
                  <span className="text-sm text-white/80">{feature}</span>
                </li>
              ))}
            </ul>
            
            <Link 
              href="/login" 
              className={`w-full py-4 rounded-xl font-bold text-center transition-all ${
                plan.popular 
                  ? 'bg-gradient-to-r from-brand-400 to-brand-600 text-white hover:shadow-lg hover:shadow-brand-500/25' 
                  : 'bg-white/10 text-white hover:bg-white/20'
              }`}
            >
              {plan.cta}
            </Link>
          </motion.div>
        ))}
      </div>
    </main>
  );
}
