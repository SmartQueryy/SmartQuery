"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { CloudArrowUpIcon, ChatBubbleLeftRightIcon, MagnifyingGlassIcon, ChartBarIcon, ShieldCheckIcon, TableCellsIcon } from "@heroicons/react/24/outline";

const FEATURES = [
  { label: "Upload CSVs Instantly", icon: <CloudArrowUpIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "Ask Data Questions", icon: <ChatBubbleLeftRightIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "AI-Powered Insights", icon: <MagnifyingGlassIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "Visualize Results", icon: <ChartBarIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "Secure & Private", icon: <ShieldCheckIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
  { label: "No SQL Needed", icon: <TableCellsIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" /> },
];

function useFirstVisit() {
  const [isFirstVisit, setIsFirstVisit] = useState(false);
  useEffect(() => {
    if (typeof window !== "undefined") {
      const visited = localStorage.getItem("smartquery_visited");
      if (!visited) {
        setIsFirstVisit(true);
        localStorage.setItem("smartquery_visited", "1");
      }
    }
  }, []);
  return isFirstVisit;
}

const DEMO_PROJECTS = [
  { name: "Sales Data", status: "Ready", rows: 1200 },
  { name: "Customer Feedback", status: "Processing", rows: 500 },
  { name: "Demo Project", status: "Ready", rows: 100 },
];

export default function LandingPage() {
  const [showFeatures, setShowFeatures] = useState(false);
  const isFirstVisit = useFirstVisit();

  return (
    <div className="w-screen h-screen flex flex-col md:flex-row overflow-hidden select-none">
      {/* Left: Logo, SmartQuery, Hero, Arrow, Features, Onboarding */}
      <div className="flex flex-col justify-center w-full md:w-1/2 bg-white dark:bg-gray-900 px-6 md:px-16 py-10 md:py-0 relative">
        {/* Logo + SmartQuery */}
        <div className="flex items-center gap-4 mb-8">
          <Image src="/smartquery-logo.svg" alt="SmartQuery Logo" width={64} height={64} className="w-14 h-14 md:w-16 md:h-16 lg:w-20 lg:h-20" />
          <span className="text-3xl md:text-4xl lg:text-5xl font-bold text-indigo-700 dark:text-indigo-400 tracking-tight">SmartQuery</span>
        </div>
        {/* Hero Section */}
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-3 text-left">Query your data, naturally.</h2>
        <p className="text-base md:text-lg lg:text-xl text-gray-700 dark:text-gray-200 mb-4 text-left">
          Upload CSV files and analyze them in plain English. Get instant answers, charts, and insights! All with no SQL or coding required.
        </p>
        {/* Onboarding Banner for First Visit */}
        {isFirstVisit && (
          <div className="bg-indigo-50 dark:bg-indigo-900/60 border border-indigo-200 dark:border-indigo-700 rounded-xl p-4 mb-4 shadow flex flex-col gap-2 animate-fade-in">
            <div className="font-semibold text-indigo-700 dark:text-indigo-200 text-lg flex items-center gap-2">
              <span role="img" aria-label="wave">👋</span> Welcome to SmartQuery!
            </div>
            <ul className="list-disc pl-6 text-indigo-800 dark:text-indigo-100 text-base mt-1">
              <li>Upload CSVs and get instant schema analysis</li>
              <li>Ask questions in plain English, no SQL needed</li>
              <li>Visualize your data with beautiful charts</li>
              <li>All your projects in one secure dashboard</li>
            </ul>
          </div>
        )}
        {/* Arrow Button */}
        <button
          aria-label="Show features"
          className="group flex items-center gap-2 focus:outline-none mb-2 mt-2"
          onClick={() => setShowFeatures(v => !v)}
          tabIndex={0}
        >
          <span className={`transition-transform duration-300 text-indigo-600 dark:text-indigo-400 text-3xl font-bold select-none ${showFeatures ? 'rotate-180' : ''}`}>^</span>
          <span className="text-sm text-indigo-600 dark:text-indigo-400 opacity-80 font-medium">See what you can do</span>
        </button>
        {/* Features List Animation */}
        <div
          className={`transition-all duration-500 ease-in-out ${showFeatures ? 'opacity-100 max-h-[400px] mt-2' : 'opacity-0 max-h-0 overflow-hidden'}`}
        >
          <ul className="bg-white/95 dark:bg-gray-900/95 rounded-xl shadow-xl px-6 md:px-8 py-6 space-y-4 border border-indigo-100 dark:border-indigo-900 backdrop-blur-md min-w-[180px] md:min-w-[220px]">
            {FEATURES.map((f, i) => (
              <li key={f.label} className={`flex items-center gap-3 text-base md:text-lg font-medium text-indigo-700 dark:text-indigo-300 tracking-wide animate-float`} style={{ animationDelay: `${i * 0.07}s` }}>
                {f.icon}
                {f.label}
              </li>
            ))}
          </ul>
        </div>
      </div>
      {/* Right: Indigo background with Dashboard Preview and CTA */}
      <div className="md:flex flex-col justify-center items-end w-full md:w-1/2 bg-indigo-600 dark:bg-indigo-400 px-0 md:px-16 py-0 md:py-0 relative">
        {/* Dashboard Preview */}
        <div className="hidden md:flex flex-col gap-8 w-full max-w-lg mx-auto mt-16">
          {/* Demo Project Cards */}
          <div className="bg-white/90 dark:bg-gray-900/90 rounded-xl shadow-lg p-6 mb-2">
            <div className="font-semibold text-lg text-indigo-700 dark:text-indigo-200 mb-2">Project Preview</div>
            <div className="flex flex-col gap-2">
              {DEMO_PROJECTS.map((proj) => (
                <div key={proj.name} className="flex items-center justify-between px-3 py-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/40">
                  <span className="font-medium text-indigo-800 dark:text-indigo-100">{proj.name}</span>
                  <span className="text-xs px-2 py-1 rounded bg-indigo-200 dark:bg-indigo-700 text-indigo-900 dark:text-indigo-100">{proj.status}</span>
                  <span className="text-xs text-indigo-700 dark:text-indigo-200">{proj.rows} rows</span>
                </div>
              ))}
            </div>
          </div>
          {/* Demo Chat Widget */}
          <div className="bg-white/90 dark:bg-gray-900/90 rounded-xl shadow-lg p-6 mb-2">
            <div className="font-semibold text-lg text-indigo-700 dark:text-indigo-200 mb-2">Ask a Question</div>
            <div className="flex items-center gap-2">
              <ChatBubbleLeftRightIcon className="h-6 w-6 text-indigo-500" />
              <span className="text-indigo-900 dark:text-indigo-100">&quot;Show me total sales by month&quot;</span>
            </div>
            <div className="mt-2 text-sm text-indigo-700 dark:text-indigo-200">Get instant answers from your data.</div>
          </div>
          {/* Demo Chart Widget */}
          <div className="bg-white/90 dark:bg-gray-900/90 rounded-xl shadow-lg p-6 mb-4">
            <div className="font-semibold text-lg text-indigo-700 dark:text-indigo-200 mb-2">Chart Preview</div>
            <div className="w-full h-32 bg-indigo-100 dark:bg-indigo-800 rounded flex items-center justify-center">
              <ChartBarIcon className="h-12 w-12 text-indigo-400 dark:text-indigo-300" />
              <span className="ml-4 text-indigo-700 dark:text-indigo-100 font-medium">Bar chart: Sales by Month</span>
            </div>
          </div>
          {/* Get Started Button (always visible under chart preview) */}
          <button
            onClick={() => window.location.href = "/login"}
            className="block w-full text-white text-2xl md:text-3xl lg:text-4xl font-bold tracking-tight cursor-pointer transition-opacity duration-200 hover:opacity-80 hover:underline focus:outline-none bg-indigo-700 dark:bg-indigo-500 py-4 rounded-xl shadow-lg mb-2"
            style={{ minWidth: 140 }}
          >
            Get Started
          </button>
        </div>
        {/* Mobile: Fixed bar at bottom */}
        <div className="block md:hidden w-full fixed bottom-0 left-0 bg-indigo-600 dark:bg-indigo-400 h-24 flex items-center justify-center z-50">
          <button
            onClick={() => window.location.href = "/login"}
            className="text-white text-2xl font-bold tracking-tight cursor-pointer transition-opacity duration-200 hover:opacity-80 hover:underline focus:outline-none"
            style={{ minWidth: 100 }}
          >
            Get Started
          </button>
        </div>
      </div>
      <style>{`
        html, body, #root { height: 100%; overflow: hidden; }
        @media (max-width: 767px) {
          .min-w-[180px] { min-width: 0 !important; }
        }
      `}</style>
    </div>
  );
}
