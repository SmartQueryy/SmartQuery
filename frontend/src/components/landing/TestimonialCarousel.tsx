"use client";

import { useState } from "react";
import { Quote, Star } from "lucide-react";
import { cn } from "@/lib/utils";

const testimonials = [
  {
    name: "Alex M.",
    role: "Data Analyst",
    avatar: "AM",
    content:
      "Finally, I can answer ad-hoc questions from my team without writing SQL. Upload the CSV, ask in English, done. Huge time saver.",
    rating: 5,
  },
  {
    name: "Jordan K.",
    role: "Product Manager",
    avatar: "JK",
    content:
      "We use SmartQuery for customer feedback CSVs. Non-technical folks can explore the data themselves. Game changer for our weekly reviews.",
    rating: 5,
  },
  {
    name: "Sam R.",
    role: "Founder",
    avatar: "SR",
    content:
      "No more back-and-forth with our dev for simple data questions. I upload our metrics CSV and get charts in seconds. Worth every penny.",
    rating: 5,
  },
  {
    name: "Taylor L.",
    role: "Operations",
    avatar: "TL",
    content:
      "The AI suggestions are surprisingly good. It understood our column names and suggested the exact questions we needed. Highly recommend.",
    rating: 5,
  },
];

export function TestimonialCarousel({ className }: { className?: string }) {
  const [isPaused, setIsPaused] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const duplicated = [...testimonials, ...testimonials];

  return (
    <div className={cn("relative overflow-hidden py-4", className)}>
      <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-white dark:from-gray-900 to-transparent z-10 pointer-events-none" aria-hidden />
      <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-white dark:from-gray-900 to-transparent z-10 pointer-events-none" aria-hidden />
      <div
        className={cn("flex gap-6", !isPaused && "animate-scroll-right")}
        style={{ width: "max-content" }}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => {
          setIsPaused(false);
          setExpandedIndex(null);
        }}
      >
        {duplicated.map((t, index) => (
          <div
            key={`${t.name}-${index}`}
            onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
            className={cn(
              "group relative flex-shrink-0 w-[380px] bg-gray-50 dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700 cursor-pointer transition-all duration-300 ease-out",
              expandedIndex === index
                ? "scale-[1.02] shadow-xl bg-white dark:bg-gray-800 border-indigo-200 dark:border-indigo-800 z-20"
                : "hover:bg-white dark:hover:bg-gray-800 hover:shadow-md hover:border-indigo-100 dark:hover:border-indigo-900 hover:-translate-y-1"
            )}
          >
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-600 to-indigo-700 flex items-center justify-center text-white font-semibold text-sm">
                {t.avatar}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 dark:text-white">{t.name}</h4>
                <p className="text-sm text-gray-500 dark:text-gray-400">{t.role}</p>
              </div>
              <Quote className="h-8 w-8 text-gray-200 dark:text-gray-600 flex-shrink-0" aria-hidden />
            </div>
            <div className="flex gap-0.5 mb-3" aria-label={`${t.rating} out of 5 stars`}>
              {[...Array(t.rating)].map((_, i) => (
                <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" aria-hidden />
              ))}
            </div>
            <p
              className={cn(
                "text-gray-600 dark:text-gray-400 text-sm leading-relaxed transition-all duration-300",
                expandedIndex === index ? "line-clamp-none" : "line-clamp-3"
              )}
            >
              &quot;{t.content}&quot;
            </p>
          </div>
        ))}
      </div>
      {expandedIndex !== null && (
        <div
          className="fixed inset-0 bg-black/20 z-30 backdrop-blur-sm"
          onClick={() => setExpandedIndex(null)}
          onKeyDown={(e) => e.key === "Escape" && setExpandedIndex(null)}
          role="button"
          tabIndex={0}
          aria-label="Close testimonial"
        />
      )}
    </div>
  );
}
