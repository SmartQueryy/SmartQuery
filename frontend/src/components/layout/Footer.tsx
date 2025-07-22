import React from "react";

const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-base-100 border-t border-base-200 px-4 py-2 text-center text-sm text-base-content/60">
      &copy; {new Date().getFullYear()} SmartQuery. All rights reserved.
    </footer>
  );
};

export default Footer; 