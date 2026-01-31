"use client";

import Link from "next/link";
import { Navbar } from "@/components/landing/Navbar";
import { PricingSection } from "@/components/landing/PricingSection";
import { TrustSection } from "@/components/landing/TrustSection";
import { Footer } from "@/components/landing/Footer";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

const comparisonRows = [
  { feature: "Projects", free: "2", pro: "15", enterprise: "Unlimited" },
  { feature: "AI queries/month", free: "25", pro: "500", enterprise: "Unlimited" },
  { feature: "File size", free: "10MB", pro: "100MB", enterprise: "Unlimited" },
  { feature: "Charts & export", free: "✓", pro: "✓", enterprise: "✓" },
  { feature: "Email support", free: "—", pro: "✓", enterprise: "✓" },
  { feature: "API access", free: "—", pro: "—", enterprise: "✓" },
  { feature: "SSO / SAML", free: "—", pro: "—", enterprise: "✓" },
  { feature: "Dedicated support", free: "—", pro: "—", enterprise: "✓" },
];

const faqs = [
  {
    q: "Can I change plans later?",
    a: "Yes. You can upgrade or downgrade at any time. When upgrading, we prorate the difference. When downgrading, the new rate applies at the next billing cycle.",
  },
  {
    q: "What payment methods do you accept?",
    a: "We accept all major credit and debit cards (Visa, Mastercard, American Express) through Stripe. Enterprise customers can also pay by invoice.",
  },
  {
    q: "Is there a free trial for Pro?",
    a: "Yes. New Pro subscribers get a 14-day free trial. No credit card required to start. You can cancel anytime during the trial.",
  },
  {
    q: "What happens to my data if I cancel?",
    a: "Your data remains available for 30 days after cancellation. You can export your projects and results during that period. After 30 days, data is permanently deleted.",
  },
  {
    q: "Do you offer annual billing?",
    a: "Yes. Annual billing saves 20% compared to monthly. Pro is $15.20/month when billed annually ($182.40/year).",
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Navbar />
      <main className="pt-16">
        <section className="py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white">
              Pricing
            </h1>
            <p className="mt-4 text-xl text-gray-600 dark:text-gray-400">
              Simple, transparent pricing. Start free, upgrade when you need more.
            </p>
          </div>
        </section>
        <PricingSection showAnnualToggle={true} />
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-900">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
              Feature comparison
            </h2>
            <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                    <th className="px-4 py-3 font-semibold text-gray-900 dark:text-white">
                      Feature
                    </th>
                    <th className="px-4 py-3 font-semibold text-gray-900 dark:text-white">
                      Free
                    </th>
                    <th className="px-4 py-3 font-semibold text-indigo-600 dark:text-indigo-400">
                      Pro
                    </th>
                    <th className="px-4 py-3 font-semibold text-gray-900 dark:text-white">
                      Enterprise
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonRows.map((row, i) => (
                    <tr
                      key={row.feature}
                      className={cn(
                        "border-b border-gray-100 dark:border-gray-800",
                        i % 2 === 1 && "bg-gray-50/50 dark:bg-gray-800/30"
                      )}
                    >
                      <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">
                        {row.feature}
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                        {row.free}
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                        {row.pro}
                      </td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                        {row.enterprise}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900/50">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
              Frequently asked questions
            </h2>
            <div className="space-y-2">
              {faqs.map((faq) => (
                <details
                  key={faq.q}
                  className="group rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden"
                >
                  <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-4 font-medium text-gray-900 dark:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500">
                    {faq.q}
                    <span className="ml-2 shrink-0 text-gray-500 transition group-open:rotate-180">
                      ▼
                    </span>
                  </summary>
                  <div className="px-4 pb-4 pt-0 text-gray-600 dark:text-gray-400">
                    {faq.a}
                  </div>
                </details>
              ))}
            </div>
          </div>
        </section>
        <TrustSection />
        <section className="py-16 px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            All payments are securely processed by Stripe.
          </p>
          <Button className="bg-indigo-600 hover:bg-indigo-700" asChild>
            <Link href="/login">Get Started Free</Link>
          </Button>
        </section>
        <Footer />
      </main>
    </div>
  );
}
