import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "HSBVectoAI | Smart Design for CorelDRAW",
  description: "Accelerate your CorelDRAW workflow with AI-powered design automation, instant vectors, and intelligent asset generation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${outfit.variable} antialiased bg-surface-950 text-white selection:bg-brand-500/30 selection:text-brand-50 min-h-screen flex flex-col`}>
        {children}
      </body>
    </html>
  );
}
