"use client";

import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { FeatureCarousel } from "@/components/landing/FeatureCarousel";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { TestimonialCarousel } from "@/components/landing/TestimonialCarousel";
import { PricingSection } from "@/components/landing/PricingSection";
import { TrustSection } from "@/components/landing/TrustSection";
import { CTASection } from "@/components/landing/CTASection";
import { Footer } from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Navbar />
      <main>
        <Hero />
        <section id="features" className="py-20 bg-gray-50 dark:bg-gray-900/50 overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
                Why SmartQuery?
              </h2>
              <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Upload CSVs, ask in plain English, get instant answers and charts.
              </p>
            </div>
          </div>
          <FeatureCarousel />
        </section>
        <HowItWorks />
        <section className="py-20 bg-white dark:bg-gray-900 overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
                Trusted by data teams
              </h2>
              <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                See what others say about querying data in plain English.
              </p>
            </div>
          </div>
          <TestimonialCarousel />
        </section>
        <PricingSection />
        <TrustSection />
        <CTASection />
        <Footer />
      </main>
    </div>
  );
}
