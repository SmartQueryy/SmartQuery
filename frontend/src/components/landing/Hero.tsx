"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Sparkles, ArrowRight, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

export function Hero({ className }: { className?: string }) {
  return (
    <section
      className={cn(
        "pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-900",
        className
      )}
    >
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-full px-4 py-1.5 text-sm font-medium text-indigo-700 dark:text-indigo-300 mb-8 animate-fade-up">
            <Sparkles className="h-4 w-4" aria-hidden />
            <span>AI-Powered CSV Analysis</span>
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-gray-900 dark:text-white animate-fade-up" style={{ animationDelay: "50ms" }}>
            Query your data in{" "}
            <span className="bg-gradient-to-r from-indigo-600 to-indigo-400 bg-clip-text text-transparent">
              plain English
            </span>
          </h1>
          <p
            className="mt-8 text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto animate-fade-up"
            style={{ animationDelay: "100ms" }}
          >
            Upload CSV files and analyze them with natural language. Get instant answers, charts, and insights—no SQL or coding required.
          </p>
          <div
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-up"
            style={{ animationDelay: "150ms" }}
          >
            <Button size="lg" className="h-12 px-8 text-base bg-indigo-600 hover:bg-indigo-700" asChild>
              <Link href="/login">
                Start Free
                <ArrowRight className="ml-2 h-5 w-5" aria-hidden />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="h-12 px-8 text-base" asChild>
              <Link href="#how-it-works">See How It Works</Link>
            </Button>
          </div>
          <div
            className="mt-8 flex flex-wrap items-center justify-center gap-4 text-sm text-gray-600 dark:text-gray-400 animate-fade-up"
            style={{ animationDelay: "200ms" }}
          >
            <div className="flex items-center gap-1">
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" aria-hidden />
              <span>Free to start</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" aria-hidden />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" aria-hidden />
              <span>AI-powered insights</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" aria-hidden />
              <span>Charts & export</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
