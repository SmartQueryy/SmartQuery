"use client";

import { Shield, Lock } from "lucide-react";
import { cn } from "@/lib/utils";

export function TrustSection({ className }: { className?: string }) {
  return (
    <section className={cn("py-12 bg-white dark:bg-gray-900 border-y border-gray-200 dark:border-gray-800", className)}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Stripe</span>
            <span className="text-sm font-medium">— Payments secured by Stripe</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <Shield className="h-5 w-5 text-indigo-600 dark:text-indigo-400" aria-hidden />
            <span className="text-sm font-medium">Your data stays private</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <Lock className="h-5 w-5 text-indigo-600 dark:text-indigo-400" aria-hidden />
            <span className="text-sm font-medium">Encrypted in transit</span>
          </div>
        </div>
      </div>
    </section>
  );
}
