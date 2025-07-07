"use client";

import SampleChart from '../components/SampleChart';
import { useCounterStore } from '../lib/store';

export default function HomePage() {
  const { count, increment, decrement } = useCounterStore();

  return (
    <main className="p-8 space-y-8">
      <h1 className="text-3xl font-bold">SmartQuery Starter</h1>
      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Zustand Counter Example</h2>
        <div className="flex items-center gap-4">
          <button className="btn btn-primary" onClick={decrement}>-</button>
          <span className="text-2xl font-mono">{count}</span>
          <button className="btn btn-primary" onClick={increment}>+</button>
        </div>
      </section>
      <section>
        <h2 className="text-xl font-semibold mb-2">Recharts Example</h2>
        <SampleChart />
      </section>
    </main>
  );
}
