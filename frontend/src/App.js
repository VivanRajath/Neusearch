import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ProductCard from './components/ProductCard';
import ProductDetail from './components/ProductDetail';
import ChatInterface from './components/ChatInterface';
import { ShoppingBag } from 'lucide-react';

const Home = () => {
  const [products, setProducts] = useState([]);
  const [activeTab, setActiveTab] = useState('All');
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 12;

  useEffect(() => {
    fetch('http://127.0.0.1:8000/products')
      .then(res => res.json())
      .then(data => {
        // Sort: Products with images and price > 0 come first
        const sortedData = data.sort((a, b) => {
          try {
            const aHasImg = a.images && a.images.length > 0;
            const bHasImg = b.images && b.images.length > 0;

            // Safely parse price
            const aPrice = a.price ? parseFloat(a.price.toString().replace(/[^0-9.]/g, '')) : 0;
            const bPrice = b.price ? parseFloat(b.price.toString().replace(/[^0-9.]/g, '')) : 0;

            const aValidPrice = !isNaN(aPrice) && aPrice > 0;
            const bValidPrice = !isNaN(bPrice) && bPrice > 0;

            if (aHasImg && aValidPrice && (!bHasImg || !bValidPrice)) return -1;
            if ((!aHasImg || !aValidPrice) && bHasImg && bValidPrice) return 1;
            return 0;
          } catch (e) {
            console.warn("Sorting error:", e);
            return 0;
          }
        });
        setProducts(sortedData);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching products:", err);
        setLoading(false);
      });
  }, []);

  // Reset page when tab changes
  useEffect(() => {
    setCurrentPage(1);
  }, [activeTab]);

  const filteredProducts = activeTab === 'All'
    ? products
    : products.filter(p => p.source === activeTab);

  // Pagination Logic
  const indexOfLastProduct = currentPage * productsPerPage;
  const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
  const currentProducts = filteredProducts.slice(indexOfFirstProduct, indexOfLastProduct);
  const totalPages = Math.ceil(filteredProducts.length / productsPerPage);

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="home-page">
      <header className="hero-section">
        <h1>Find Your Perfect Match</h1>
        <p>Discover premium products from Hunnit and Traya curated just for you.</p>
      </header>

      <div className="tabs-container">
        {['All', 'Hunnit', 'Traya'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="product-grid">
        {loading ? (
          <p className="loading">Loading products...</p>
        ) : currentProducts.length > 0 ? (
          currentProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))
        ) : (
          <p className="no-products">No products found in this category.</p>
        )}
      </div>

      {/* Pagination Controls */}
      {!loading && totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
            className="page-btn"
          >
            Previous
          </button>

          {[...Array(totalPages)].map((_, i) => {
            // Show limited page numbers for cleaner UI
            if (
              i + 1 === 1 ||
              i + 1 === totalPages ||
              (i + 1 >= currentPage - 1 && i + 1 <= currentPage + 1)
            ) {
              return (
                <button
                  key={i}
                  onClick={() => paginate(i + 1)}
                  className={`page-btn ${currentPage === i + 1 ? 'active' : ''}`}
                >
                  {i + 1}
                </button>
              );
            } else if (
              (i + 1 === currentPage - 2 && currentPage > 3) ||
              (i + 1 === currentPage + 2 && currentPage < totalPages - 2)
            ) {
              return <span key={i} className="dots">...</span>;
            }
            return null;
          })}

          <button
            onClick={() => paginate(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="page-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="logo">
            <ShoppingBag size={24} />
            <span>AI Shopping Assistant</span>
          </div>
          <div className="nav-links">
            <Link to="/">Home</Link>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/product/:id" element={<ProductDetail />} />
          </Routes>
        </main>

        <ChatInterface />
      </div>
    </Router>
  );
}

export default App;
