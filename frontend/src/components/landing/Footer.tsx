"use client";

import Link from "next/link";
import Image from "next/image";
import { Mail, Github, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

export function Footer({ className }: { className?: string }) {
  return (
    <footer className={cn("border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900", className)}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Image
                src="/smartquery-logo.svg"
                alt="SmartQuery"
                width={40}
                height={40}
                className="w-10 h-10"
              />
              <span className="text-xl font-bold text-indigo-700 dark:text-indigo-400">
                SmartQuery
              </span>
            </Link>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              AI-powered CSV analysis. Query your data in plain English.
            </p>
            <div className="mt-4 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <Shield className="h-4 w-4 text-indigo-600 dark:text-indigo-400" aria-hidden />
              <span>Payments securely processed by Stripe</span>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Product</h4>
            <ul className="space-y-3">
              <li>
                <Link href="#features" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="#how-it-works" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                  How it works
                </Link>
              </li>
              <li>
                <Link href="/login" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Resources</h4>
            <ul className="space-y-3">
              <li>
                <Link href="/terms" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Connect</h4>
            <div className="flex flex-col gap-3">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-4 w-4" aria-hidden />
                GitHub
              </a>
              <a
                href="mailto:support@smartquery.ai"
                className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                aria-label="Email"
              >
                <Mail className="h-4 w-4" aria-hidden />
                Contact
              </a>
            </div>
          </div>
        </div>
        <div className="py-6 border-t border-gray-200 dark:border-gray-800">
          <p className="text-sm text-gray-500 dark:text-gray-500 text-center">
            © {new Date().getFullYear()} SmartQuery. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
