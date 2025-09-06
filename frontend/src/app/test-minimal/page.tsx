'use client';

import React from 'react';

export default function TestMinimalPage() {
  console.log('TestMinimalPage render');

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Minimal Test Page</h1>
      <p>This page has no Zustand store usage at all.</p>
    </div>
  );
}