"use client";

import Link from "next/link";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Navbar />
      <main className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto prose prose-gray dark:prose-invert prose-headings:font-bold prose-a:text-indigo-600 dark:prose-a:text-indigo-400">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Privacy Policy
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
            Last updated: {new Date().toLocaleDateString("en-US")}
          </p>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              1. Information We Collect
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
              We collect information you provide directly (e.g., when you sign up or contact us) and
              information we get when you use the Service:
            </p>
            <ul className="list-disc pl-6 text-gray-600 dark:text-gray-400 space-y-2">
              <li>
                <strong>Account data:</strong> name, email, profile picture (from Google OAuth when you sign in)
              </li>
              <li>
                <strong>Usage data:</strong> projects, queries, and how you use the Service
              </li>
              <li>
                <strong>Data you upload:</strong> CSV files and their contents, which we process to provide the Service
              </li>
              <li>
                <strong>Payment data:</strong> processed by Stripe; we do not store full card numbers
              </li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              2. How We Use Your Information
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              We use the information to provide, maintain, and improve the Service; to process payments;
              to send you product updates and support; to protect the Service and our users; and to
              comply with legal obligations. We do not sell your personal information.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              3. Third-Party Services
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
              We use the following third-party services, each with their own privacy practices:
            </p>
            <ul className="list-disc pl-6 text-gray-600 dark:text-gray-400 space-y-2">
              <li>
                <strong>Google:</strong> for sign-in (OAuth). Google&apos;s privacy policy applies to data shared with Google.
              </li>
              <li>
                <strong>Stripe:</strong> for payment processing. Card details are handled by Stripe; we receive only transaction and billing information needed to provide the Service.
              </li>
              <li>
                <strong>AI/ML providers:</strong> we may send query text and schema (not raw file contents) to providers to power natural-language-to-SQL and suggestions.
              </li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              4. Cookies and Similar Technologies
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              We use cookies and similar technologies for authentication, preferences, and analytics.
              You can control cookies through your browser settings. Disabling certain cookies may
              affect the functionality of the Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              5. Data Retention and Deletion
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              We retain your data for as long as your account is active or as needed to provide the
              Service and comply with law. You may request deletion of your account and associated data;
              we will delete or anonymize it within a reasonable period, except where we must retain
              it for legal or operational reasons.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              6. Your Rights
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Depending on your location, you may have the right to access, correct, delete, or port
              your personal data, or to object to or restrict certain processing. To exercise these
              rights, contact us at the email below. You may also have the right to lodge a complaint
              with a supervisory authority.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              7. Security
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              We use industry-standard measures to protect your data, including encryption in transit
              and at rest, access controls, and secure infrastructure. No method of transmission or
              storage is 100% secure; we cannot guarantee absolute security.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              8. Children
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              The Service is not intended for users under 16. We do not knowingly collect personal
              information from children under 16. If you believe we have collected such information,
              please contact us so we can delete it.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              9. Changes
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              We may update this Privacy Policy from time to time. We will post the updated policy
              on this page and update the &quot;Last updated&quot; date. Continued use of the Service after
              changes constitutes acceptance. For material changes, we may provide additional notice.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">
              10. Contact
            </h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              For privacy-related questions or requests, contact us at{" "}
              <a href="mailto:privacy@smartquery.ai" className="text-indigo-600 dark:text-indigo-400 hover:underline">
                privacy@smartquery.ai
              </a>
              . You can also review our{" "}
              <Link href="/terms">Terms of Service</Link> for more information about your use of the Service.
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
