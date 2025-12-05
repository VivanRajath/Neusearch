import React from 'react';
import { Link } from 'react-router-dom';

const ProductCard = ({ product }) => {
  return (
    <div className="product-card">
      <div className="image-container">
        <img
          src={product.images ? product.images.split(',')[0].trim() : 'https://placehold.co/300'}
          alt={product.title}
          onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/300?text=No+Image'; }}
        />
      </div>
      <div className="product-info">
        <h3>{product.title}</h3>
        <p className="price">₹{product.price}</p>
        <p className="category">{product.category}</p>
        <Link to={`/product/${product.id}`} className="view-btn">View Details</Link>
      </div>
    </div>
  );
};

export default ProductCard;
