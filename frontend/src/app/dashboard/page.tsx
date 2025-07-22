/**
 * Dashboard Page
 * 
 * Protected dashboard page that shows user information and logout functionality.
 */

"use client";

import React from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/components/auth/AuthProvider';
import { CloudArrowUpIcon, FolderOpenIcon, QuestionMarkCircleIcon } from "@heroicons/react/24/outline";

function DashboardContent() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="fixed inset-0 min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-indigo-100 via-indigo-200 to-indigo-300 dark:from-gray-900 dark:via-indigo-950 dark:to-indigo-900 overflow-hidden select-none">
      <div className="w-full max-w-4xl mx-auto flex flex-col gap-8 p-6">
        {/* Welcome Header */}
        <div className="flex flex-col items-center gap-2 mb-2">
          <h1 className="text-3xl md:text-4xl font-bold text-indigo-700 dark:text-indigo-400 tracking-tight">Welcome back, {user?.name || 'User'}!</h1>
          <p className="text-base md:text-lg text-gray-700 dark:text-gray-200">Your SmartQuery dashboard</p>
        </div>
        {/* User Info Card */}
        <div className="w-full bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col gap-4">
          <h3 className="text-lg font-semibold text-indigo-700 dark:text-indigo-200 mb-2">User Information</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Name</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Email</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">User ID</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.id}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Member Since</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</dd>
            </div>
          </div>
        </div>
        {/* Stats Cards */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col items-center">
            <div className="w-12 h-12 bg-indigo-200 dark:bg-indigo-700 rounded-full flex items-center justify-center mb-2">
              <FolderOpenIcon className="w-7 h-7 text-indigo-700 dark:text-indigo-200" />
            </div>
            <div className="text-lg font-semibold text-indigo-700 dark:text-indigo-200">Total Projects</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">0</div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col items-center">
            <div className="w-12 h-12 bg-green-200 dark:bg-green-700 rounded-full flex items-center justify-center mb-2">
              <CloudArrowUpIcon className="w-7 h-7 text-green-700 dark:text-green-200" />
            </div>
            <div className="text-lg font-semibold text-green-700 dark:text-green-200">Ready Projects</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">0</div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col items-center">
            <div className="w-12 h-12 bg-yellow-200 dark:bg-yellow-700 rounded-full flex items-center justify-center mb-2">
              <QuestionMarkCircleIcon className="w-7 h-7 text-yellow-700 dark:text-yellow-200" />
            </div>
            <div className="text-lg font-semibold text-yellow-700 dark:text-yellow-200">Processing</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">0</div>
          </div>
        </div>
        {/* Quick Actions */}
        <div className="w-full bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col gap-4">
          <h3 className="text-lg font-semibold text-indigo-700 dark:text-indigo-200 mb-2">Quick Actions</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <button className="w-full py-3 rounded-xl bg-indigo-700 dark:bg-indigo-500 text-white font-semibold text-base hover:bg-indigo-800 dark:hover:bg-indigo-600 transition-colors flex items-center justify-center gap-2">
              <CloudArrowUpIcon className="w-5 h-5" />
              Upload CSV File
            </button>
            <button className="w-full py-3 rounded-xl bg-indigo-200 dark:bg-indigo-700 text-indigo-900 dark:text-white font-semibold text-base hover:bg-indigo-300 dark:hover:bg-indigo-600 transition-colors flex items-center justify-center gap-2">
              <FolderOpenIcon className="w-5 h-5" />
              View Projects
            </button>
            <button className="w-full py-3 rounded-xl bg-white dark:bg-gray-900 border border-indigo-300 dark:border-indigo-700 text-indigo-700 dark:text-indigo-200 font-semibold text-base hover:bg-indigo-50 dark:hover:bg-indigo-800 transition-colors flex items-center justify-center gap-2">
              <QuestionMarkCircleIcon className="w-5 h-5" />
              Get Help
            </button>
          </div>
        </div>
        {/* Sign Out Button */}
        <div className="flex justify-center mt-4">
          <button
            onClick={handleLogout}
            className="py-2 px-6 rounded-xl bg-red-500 text-white font-semibold text-base hover:bg-red-600 transition-colors shadow"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
} 