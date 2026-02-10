'use client';

import { usePathname } from 'next/navigation';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

export default function AppChrome({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const showAppChrome =
    pathname?.startsWith('/dashboard') ||
    pathname?.startsWith('/projects') ||
    pathname?.startsWith('/workspace');

  if (showAppChrome) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-6 bg-base-100">{children}</main>
        </div>
        <Footer />
      </div>
    );
  }

  return <>{children}</>;
}
