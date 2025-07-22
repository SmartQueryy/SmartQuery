import React from "react";

const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 h-full bg-base-200 border-r border-base-300 flex flex-col p-4">
      <div className="mb-4 font-semibold text-base-content/80">Projects</div>
      <nav className="flex-1">
        {/* Project navigation placeholder */}
        <ul className="menu">
          <li><a className="active">Project 1</a></li>
          <li><a>Project 2</a></li>
          <li><a>Project 3</a></li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar; 