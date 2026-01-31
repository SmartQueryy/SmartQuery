"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Zap, Sparkles, Building2, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const tiers = [
  {
    name: "Free",
    price: { monthly: 0, annual: 0 },
    description: "Perfect for trying out",
    icon: Zap,
    features: [
      "2 projects",
      "25 AI queries/month",
      "10MB per file",
      "Core features",
      "Community support",
    ],
    cta: "Get Started Free",
    href: "/login",
    variant: "outline" as const,
    popular: false,
  },
  {
    name: "Pro",
    price: { monthly: 19, annual: 15.2 },
    description: "For data analysts & teams",
    icon: Sparkles,
    features: [
      "15 projects",
      "500 AI queries/month",
      "100MB per file",
      "All features",
      "Email support",
      "Export options",
    ],
    cta: "Start Pro Trial",
    href: "/login",
    variant: "default" as const,
    popular: true,
  },
  {
    name: "Enterprise",
    price: null,
    description: "For large organizations",
    icon: Building2,
    features: [
      "Unlimited projects",
      "Unlimited queries",
      "Unlimited storage",
      "SSO / SAML",
      "API access",
      "Dedicated support",
    ],
    cta: "Contact Sales",
    href: "/login",
    variant: "outline" as const,
    popular: false,
  },
];

export function PricingSection({
  className,
  showAnnualToggle = true,
}: {
  className?: string;
  showAnnualToggle?: boolean;
}) {
  const [annual, setAnnual] = useState(false);

  return (
    <section id="pricing" className={cn("py-20 bg-gray-50 dark:bg-gray-900/50", className)}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Start free. Upgrade when you need more projects and queries.
          </p>
          {showAnnualToggle && (
            <div className="mt-6 flex items-center justify-center gap-3">
              <span className={cn("text-sm", !annual ? "font-medium text-gray-900 dark:text-white" : "text-gray-500 dark:text-gray-400")}>
                Monthly
              </span>
              <button
                type="button"
                role="switch"
                aria-checked={annual}
                onClick={() => setAnnual((v) => !v)}
                className="relative w-11 h-6 rounded-full bg-gray-200 dark:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                <span
                  className={cn(
                    "absolute top-1 left-1 w-4 h-4 rounded-full bg-white shadow transition-transform",
                    annual && "translate-x-5"
                  )}
                />
              </button>
              <span className={cn("text-sm", annual ? "font-medium text-gray-900 dark:text-white" : "text-gray-500 dark:text-gray-400")}>
                Annual
              </span>
              <Badge variant="secondary" className="text-xs">
                Save 20%
              </Badge>
            </div>
          )}
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {tiers.map((tier) => {
            const Icon = tier.icon;
            const price = tier.price
              ? annual
                ? tier.price.annual
                : tier.price.monthly
              : null;
            return (
              <div
                key={tier.name}
                className={cn(
                  "group relative bg-white dark:bg-gray-800 rounded-2xl p-8 border transition-all duration-300 ease-out",
                  tier.popular
                    ? "border-2 border-indigo-500 shadow-lg hover:shadow-xl hover:-translate-y-1"
                    : "border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-indigo-200 dark:hover:border-indigo-900 hover:-translate-y-1"
                )}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-indigo-600 hover:bg-indigo-600 text-white px-3">
                      Most Popular
                    </Badge>
                  </div>
                )}
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400">
                  <Icon className="h-6 w-6" aria-hidden />
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">{tier.name}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{tier.description}</p>
                <div className="mt-4 mb-6">
                  {price !== null ? (
                    <>
                      <span className="text-4xl font-bold text-gray-900 dark:text-white">
                        ${price}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400">/month</span>
                      {annual && tier.name === "Pro" && (
                        <span className="block text-sm text-gray-500 dark:text-gray-400 mt-1">
                          Billed annually
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="text-4xl font-bold text-gray-900 dark:text-white">Custom</span>
                  )}
                </div>
                <ul className="space-y-3 mb-8">
                  {tier.features.map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                      <Check className="h-4 w-4 text-green-500 shrink-0" aria-hidden />
                      {f}
                    </li>
                  ))}
                </ul>
                <Button
                  variant={tier.variant}
                  className={cn(
                    "w-full",
                    tier.popular && "bg-indigo-600 hover:bg-indigo-700"
                  )}
                  asChild
                >
                  <Link href={tier.href} className="flex items-center justify-center gap-2">
                    {tier.cta}
                    <ArrowRight className="h-4 w-4" aria-hidden />
                  </Link>
                </Button>
              </div>
            );
          })}
        </div>
        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          All plans include secure storage and standard support. Payments are securely processed by Stripe.
        </p>
        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-2">
          <Link href="/pricing" className="text-indigo-600 dark:text-indigo-400 hover:underline">
            View full pricing details →
          </Link>
        </p>
      </div>
    </section>
  );
}
