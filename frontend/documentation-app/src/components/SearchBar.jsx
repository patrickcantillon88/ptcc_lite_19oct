import React from 'react'

const SearchBar = ({ searchTerm, setSearchTerm }) => {
  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="🔍 Search documentation..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="search-input"
      />
      {searchTerm && (
        <button 
          onClick={() => setSearchTerm('')}
          className="search-clear"
          title="Clear search"
        >
          ✕
        </button>
      )}
    </div>
  )
}

export default SearchBar