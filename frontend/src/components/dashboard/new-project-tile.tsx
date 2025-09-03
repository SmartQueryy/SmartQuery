"use client";

import React from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';

interface NewProjectTileProps {
  onClick: () => void;
}

export function NewProjectTile({ onClick }: NewProjectTileProps) {
  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-950 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 cursor-pointer border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500 group min-h-[200px] flex items-center justify-center"
    >
      <div className="text-center">
        <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-indigo-200 dark:group-hover:bg-indigo-800 transition-colors">
          <PlusIcon className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
        </div>
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg mb-2">
          New Project
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          Upload a CSV file to get started
        </p>
      </div>
    </div>
  );
}