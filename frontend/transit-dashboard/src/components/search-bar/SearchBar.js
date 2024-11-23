import React, { useState } from 'react';
import { useMap } from 'react-leaflet';
import './SearchBar.css';

const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;; // Replace with your API key

const SearchBar = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false); // For button blocking
  const map = useMap();

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query) return;

    setLoading(true); // Block the button while searching

    try {
      const toronto_query = `${query}, Toronto, ON, Canada`
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(
            toronto_query
        )}&key=${GOOGLE_MAPS_API_KEY}`
      );

      const results = await response.json();

      if (results.status !== 'OK' || results.results.length === 0) {
        console.log(results)
        alert('No results found. Try a different query.');
        setLoading(false); // Unblock the button
        return;
      }

      const { lat, lng } = results.results[0].geometry.location;

      // Recenter the map to the search result
      map.setView([lat, lng], 15);
    } catch (error) {
      console.error('Search error:', error);
      alert('An error occurred during search. Please try again.');
    } finally {
      setLoading(false); // Unblock the button
    }
  };

  return (
    <div
      className="search-bar"
      onClick={(e) => e.stopPropagation()} // Prevent click from affecting map
    >
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search for an intersection..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  );
};

export default SearchBar;
