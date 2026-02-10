"use client";

import { Upload, MessageSquare, BarChart2 } from "lucide-react";
import { cn } from "@/lib/utils";

const steps = [
  {
    number: "01",
    title: "Upload your CSV",
    description: "Add your CSV file. We analyze the schema and make it ready for natural language queries.",
    icon: Upload,
  },
  {
    number: "02",
    title: "Ask questions naturally",
    description: "Type what you want to know in plain English. No SQL or formulas required.",
    icon: MessageSquare,
  },
  {
    number: "03",
    title: "Get instant insights",
    description: "See answers as tables and charts. Export or share results in one click.",
    icon: BarChart2,
  },
];

export function HowItWorks({ className }: { className?: string }) {
  return (
    <section id="how-it-works" className={cn("py-20 bg-white dark:bg-gray-900", className)}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
            How it works
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Three steps from CSV to insight
          </p>
        </div>
        <div className="relative">
          <div
            className="hidden md:block absolute top-12 left-[16.67%] right-[16.67%] h-0.5 bg-gradient-to-r from-gray-200 via-indigo-200 to-gray-200 dark:from-gray-700 dark:via-indigo-800 dark:to-gray-700"
            aria-hidden
          />
          <div className="grid md:grid-cols-3 gap-12 md:gap-8">
            {steps.map((step) => {
              const Icon = step.icon;
              return (
                <div key={step.number} className="relative text-center">
                  <div className="relative inline-flex items-center justify-center w-24 h-24 mb-6">
                    <div className="absolute inset-0 bg-indigo-100 dark:bg-indigo-900/40 rounded-full" />
                    <span className="relative flex items-center justify-center w-12 h-12 rounded-full bg-indigo-600 text-white">
                      <Icon className="h-6 w-6" aria-hidden />
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 max-w-xs mx-auto">
                    {step.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
