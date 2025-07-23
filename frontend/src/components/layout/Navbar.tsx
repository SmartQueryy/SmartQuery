import React from "react";
import Image from "next/image.js";

const Navbar: React.FC = () => {
  return (
    <nav className="w-full bg-base-100 border-b border-base-200 px-4 py-2 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Image src="/smartquery-logo.svg" alt="SmartQuery Logo" width={32} height={32} className="w-8 h-8" />
        <span className="font-bold text-lg tracking-tight text-indigo-700 dark:text-indigo-400">SmartQuery</span>
        {/* Breadcrumb navigation placeholder */}
        <span className="ml-4 text-sm text-base-content/60">Dashboard</span>
      </div>
      <div className="flex items-center gap-4">
        {/* User profile dropdown placeholder */}
        <div className="dropdown dropdown-end">
          <label tabIndex={0} className="btn btn-ghost btn-circle avatar">
            <div className="w-8 rounded-full bg-base-200" />
          </label>
          <ul tabIndex={0} className="mt-3 p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52">
            <li><a>Profile</a></li>
            <li><a>Settings</a></li>
            <li><a>Logout</a></li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 