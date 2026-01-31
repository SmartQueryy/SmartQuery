"use client";

import Link from "next/link";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Navbar />
      <main className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto prose prose-gray dark:prose-invert prose-headings:font-bold prose-a:text-indigo-600 dark:prose-a:text-indigo-400">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Terms of Service
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
            Last updated: {new Date().toLocaleDateString("en-US")}
          </p>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              1. Agreement to Terms
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              By accessing or using SmartQuery (&quot;Service&quot;), you agree to be bound by these Terms of Service.
              If you do not agree, do not use the Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              2. Description of Service
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              SmartQuery provides a platform for uploading CSV files and querying them using natural language.
              The Service includes AI-powered query conversion, visualization, and export features as described
              on our website and in your plan.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              3. Account and Registration
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              You must provide accurate information when creating an account. You are responsible for
              maintaining the security of your account and for all activity under your account. You must
              notify us immediately of any unauthorized use.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              4. Acceptable Use
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
              You agree not to:
            </p>
            <ul className="list-disc pl-6 text-gray-600 dark:text-gray-400 space-y-2">
              <li>Use the Service for any illegal purpose or in violation of applicable laws</li>
              <li>Upload data you do not have the right to use or that infringes third-party rights</li>
              <li>Attempt to gain unauthorized access to the Service or other accounts</li>
              <li>Interfere with or disrupt the Service or servers</li>
              <li>Use the Service to transmit malware or harmful code</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              5. Payment Terms
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Paid plans are billed in advance (monthly or annually). Payments are processed securely
              by Stripe. You authorize us to charge your payment method for all fees incurred. Refunds
              are handled according to our refund policy. We may change pricing with reasonable notice;
              continued use after changes constitutes acceptance.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              6. Data and Privacy
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Your use of the Service is also governed by our{" "}
              <Link href="/privacy">Privacy Policy</Link>. You retain ownership of data you upload.
              We process data as necessary to provide the Service and as described in the Privacy Policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              7. Intellectual Property
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              We own the Service, including the software, design, and branding. We grant you a limited,
              non-exclusive license to use the Service in accordance with these Terms. You may not copy,
              modify, or create derivative works of the Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              8. Limitation of Liability
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              To the maximum extent permitted by law, SmartQuery and its affiliates shall not be liable
              for any indirect, incidental, special, consequential, or punitive damages, or for loss of
              profits, data, or use. Our total liability shall not exceed the amount you paid us in the
              twelve months preceding the claim.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              9. Termination
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              We may suspend or terminate your access for violation of these Terms or for any reason
              with notice. You may cancel your account at any time. Upon termination, your right to
              use the Service ceases. Provisions that by their nature should survive (e.g., liability
              limitations, indemnity) will survive.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              10. Contact
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Questions about these Terms? Contact us at{" "}
              <a href="mailto:support@smartquery.ai" className="text-indigo-600 dark:text-indigo-400 hover:underline">
                support@smartquery.ai
              </a>
              .
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
