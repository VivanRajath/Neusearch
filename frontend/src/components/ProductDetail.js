import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import config from '../config';

const ProductDetail = () => {
    const { id } = useParams();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        setLoading(true);
        // data.id is integer in DB, so param id should be parsed if needed, 
        // but backend handles string->int conversion usually or we pass int.
        // Let's rely on loose equality or backend handling.
        // Let's rely on loose equality or backend handling.
        fetch(`${config.API_URL}/products/${id}`)
            .then(res => {
                if (!res.ok) throw new Error('Product not found');
                return res.json();
            })
            .then(data => {
                if (data.error) throw new Error(data.error);
                console.log('Product data received:', data);
                setProduct(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setError(true);
                setLoading(false);
            });
    }, [id]);

    if (loading) return (
        <div className="product-detail-page">
            <div className="loading">Loading product details...</div>
        </div>
    );

    if (error || !product) return (
        <div className="product-detail-page">
            <div className="error-container" style={{ textAlign: 'center', padding: '4rem' }}>
                <h2>Product not found</h2>
                <Link to="/" className="back-link" style={{ marginTop: '1rem', display: 'inline-block' }}>
                    <ArrowLeft size={20} /> Return Home
                </Link>
            </div>
        </div>
    );

    return (
        <div className="product-detail-page">
            <Link to="/" className="back-link"><ArrowLeft size={20} /> Back to Browse</Link>

            <div className="detail-container">
                <div className="detail-image">
                    <div className="main-image-wrapper">
                        <img
                            src={product.images ? product.images.split(',')[0].trim() : 'https://placehold.co/500'}
                            alt={product.title}
                            onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/500?text=No+Image'; }}
                        />
                    </div>
                    {product.images && product.images.split(',').length > 1 && (
                        <div className="image-gallery">
                            {product.images.split(',').map((img, idx) => (
                                <img
                                    key={idx}
                                    src={img.trim()}
                                    alt={`View ${idx + 1}`}
                                    onClick={(e) => {
                                        // Simple gallery click to swap main image could be added here
                                        const mainImg = document.querySelector('.main-image-wrapper img');
                                        if (mainImg) mainImg.src = e.target.src;
                                    }}
                                />
                            ))}
                        </div>
                    )}
                </div>

                <div className="detail-info">
                    <div className="product-header">
                        {product.category && <span className="category-badge">{product.category}</span>}
                        <h1>{product.title}</h1>
                    </div>

                    <p className="price-tag">₹{product.price}</p>
                    {product.source && <p className="source-tag">Source: {product.source}</p>}

                    <div className="description">
                        <h3>Description</h3>
                        <p>{product.description || 'No description available for this product.'}</p>
                    </div>

                    <div className="features">
                        <h3>Features</h3>
                        <ul>
                            {product.features && product.features.trim() ? (
                                product.features.split(',').map((f, idx) => (
                                    <li key={idx}>{f.trim()}</li>
                                ))
                            ) : (
                                <li>No specific features listed for this product.</li>
                            )}
                        </ul>
                    </div>

                    <a href={product.url} target="_blank" rel="noopener noreferrer" className="buy-btn">
                        Buy Now on {product.source || 'Store'}
                    </a>
                </div>
            </div>
        </div>
    );
};

export default ProductDetail;
