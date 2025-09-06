'use client';

import React from 'react';
import { useProjectActions } from '@/lib/store/project';

export default function TestActionsPage() {
  const actions = useProjectActions();
  
  console.log('TestActionsPage render', { 
    hasActions: !!actions,
    actionKeys: Object.keys(actions) 
  });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Test Actions Page</h1>
      <div>
        <p>Actions available: {Object.keys(actions).join(', ')}</p>
      </div>
    </div>
  );
}