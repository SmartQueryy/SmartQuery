"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

export function CTASection({ className }: { className?: string }) {
  return (
    <section className={cn("py-20 bg-indigo-600 dark:bg-indigo-700", className)}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to query your data in plain English?
          </h2>
          <p className="text-lg text-indigo-100 max-w-2xl mx-auto mb-8">
            Join teams who use SmartQuery to get instant insights from their CSV files—no SQL required.
          </p>
          <Button
            size="lg"
            className="h-12 px-8 text-base bg-white text-indigo-600 hover:bg-indigo-50 focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600"
            asChild
          >
            <Link href="/login">
              Get Started for Free
              <ArrowRight className="ml-2 h-5 w-5" aria-hidden />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
