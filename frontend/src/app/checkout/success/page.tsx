"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Loader2 } from "lucide-react";

function CheckoutSuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [isVerifying, setIsVerifying] = useState(!!sessionId);

  useEffect(() => {
    if (!sessionId) {
      setIsVerifying(false);
      return;
    }
    const t = setTimeout(() => setIsVerifying(false), 1500);
    return () => clearTimeout(t);
  }, [sessionId]);

  return (
    <main className="flex-1 flex items-center justify-center px-4 py-20">
      <div className="max-w-lg w-full text-center">
        <div className="mb-8">
          {isVerifying ? (
            <div className="mx-auto w-16 h-16 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
              <Loader2
                className="h-8 w-8 text-indigo-600 dark:text-indigo-400 animate-spin"
                aria-hidden
              />
            </div>
          ) : (
            <div className="mx-auto w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center">
              <CheckCircle2
                className="h-10 w-10 text-green-600 dark:text-green-400"
                aria-hidden
              />
            </div>
          )}
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {isVerifying ? "Confirming your subscription…" : "Payment successful"}
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          {isVerifying
            ? "Please wait while we verify your payment."
            : "Thank you for upgrading to SmartQuery Pro. Your account has been updated with Pro features."}
        </p>
        {!isVerifying && (
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild className="bg-indigo-600 hover:bg-indigo-700">
              <Link href="/dashboard">Go to Dashboard</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/workspace">Open Workspace</Link>
            </Button>
          </div>
        )}
      </div>
    </main>
  );
}

export default function CheckoutSuccessPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
      <Navbar />
      <Suspense
        fallback={
          <main className="flex-1 flex items-center justify-center px-4 py-20">
            <Loader2 className="h-8 w-8 text-indigo-600 animate-spin" />
          </main>
        }
      >
        <CheckoutSuccessContent />
      </Suspense>
      <Footer />
    </div>
  );
}
