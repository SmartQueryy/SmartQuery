"use client";

import { useState, useRef } from "react";
import {
  CloudUpload,
  MessageCircle,
  Search,
  BarChart3,
  ShieldCheck,
  Table2,
  Sparkles,
  FileSpreadsheet,
} from "lucide-react";
import { cn } from "@/lib/utils";

const features = [
  {
    icon: CloudUpload,
    title: "Upload CSVs Instantly",
    description: "Drag and drop your CSV files. We analyze schema and prepare your data for natural language queries.",
  },
  {
    icon: MessageCircle,
    title: "Ask Data Questions",
    description: "Type questions in plain English. Get instant answers without writing SQL or code.",
  },
  {
    icon: Search,
    title: "AI-Powered Insights",
    description: "Our AI understands your data and suggests the right questions and visualizations.",
  },
  {
    icon: BarChart3,
    title: "Visualize Results",
    description: "Charts and tables generated automatically. Export to share or embed.",
  },
  {
    icon: ShieldCheck,
    title: "Secure & Private",
    description: "Your data stays yours. Enterprise-grade security and optional private deployment.",
  },
  {
    icon: Table2,
    title: "No SQL Needed",
    description: "Natural language to SQL under the hood. You just ask; we handle the rest.",
  },
  {
    icon: Sparkles,
    title: "Smart Suggestions",
    description: "Semantic search and query suggestions based on your dataset and usage.",
  },
  {
    icon: FileSpreadsheet,
    title: "Export & Share",
    description: "Download results as CSV or view inline. Perfect for reports and dashboards.",
  },
];

export function FeatureCarousel({ className }: { className?: string }) {
  const [isPaused, setIsPaused] = useState(false);
  const duplicatedFeatures = [...features, ...features];

  return (
    <div className={cn("relative overflow-hidden py-4", className)}>
      <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-gray-50 dark:from-gray-900 to-transparent z-10 pointer-events-none" aria-hidden />
      <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-gray-50 dark:from-gray-900 to-transparent z-10 pointer-events-none" aria-hidden />
      <div
        className={cn("flex gap-6", !isPaused && "animate-scroll-left")}
        style={{ width: "max-content" }}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
        onFocus={() => setIsPaused(true)}
        onBlur={() => setIsPaused(false)}
      >
        {duplicatedFeatures.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <div
              key={`${feature.title}-${index}`}
              className="group relative flex-shrink-0 w-[320px] bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 transition-all duration-300 ease-out hover:shadow-lg hover:border-indigo-200 dark:hover:border-indigo-800 hover:-translate-y-1"
            >
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-all duration-300 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white">
                <Icon className="h-6 w-6" aria-hidden />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {feature.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
