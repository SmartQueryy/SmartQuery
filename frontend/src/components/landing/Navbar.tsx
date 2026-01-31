"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Navbar({ className }: { className?: string }) {
  return (
    <nav
      className={cn(
        "fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800",
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link
            href="/"
            className="flex items-center gap-2 transition-opacity hover:opacity-90"
            aria-label="SmartQuery home"
          >
            <Image
              src="/smartquery-logo.svg"
              alt="SmartQuery"
              width={32}
              height={32}
              className="w-8 h-8"
            />
            <span className="text-xl font-bold text-indigo-700 dark:text-indigo-400 tracking-tight">
              SmartQuery
            </span>
          </Link>
          <div className="hidden lg:flex items-center gap-8">
            <Link
              href="#features"
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Features
            </Link>
            <Link
              href="#how-it-works"
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              How it works
            </Link>
            <Link
              href="/pricing"
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Pricing
            </Link>
            <Link
              href="/terms"
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Resources
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" className="hidden sm:flex" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700" asChild>
              <Link href="/login">Get Started</Link>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
