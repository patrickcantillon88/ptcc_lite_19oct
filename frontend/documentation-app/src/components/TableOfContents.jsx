import React from 'react'

const TableOfContents = ({ sections, activeSection, setActiveSection }) => {
  return (
    <div className="toc">
      <h3>📖 Contents</h3>
      <ul className="toc-list">
        {sections.map(section => (
          <li key={section.id}>
            <button
              className={`toc-item ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => setActiveSection(section.id)}
            >
              {section.title}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default TableOfContents