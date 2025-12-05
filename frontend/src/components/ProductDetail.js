import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const ProductDetail = () => {
    const { id } = useParams();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Ideally fetch single product by ID from API
        // For now, fetching all and finding (optimization: add /products/:id endpoint)
        fetch('http://127.0.0.1:8000/products')
            .then(res => res.json())
            .then(data => {
                const found = data.find(p => p.id === parseInt(id));
                setProduct(found);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [id]);

    if (loading) return <div className="loading">Loading...</div>;
    if (!product) return <div className="error">Product not found</div>;

    return (
        <div className="product-detail-page">
            <Link to="/" className="back-link"><ArrowLeft size={20} /> Back to Browse</Link>

            <div className="detail-container">
                <div className="detail-image">
                    <img
                        src={product.images ? product.images.split(',')[0].trim() : 'https://placehold.co/500'}
                        alt={product.title}
                        onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/500?text=No+Image'; }}
                    />
                    <div className="image-gallery">
                        {product.images && product.images.split(',').map((img, idx) => (
                            <img key={idx} src={img.trim()} alt={`View ${idx + 1}`} />
                        ))}
                    </div>
                </div>

                <div className="detail-info">
                    <h1>{product.title}</h1>
                    <p className="price-tag">₹{product.price}</p>
                    <p className="source-tag">Source: {product.source}</p>

                    <div className="description">
                        <h3>Description</h3>
                        <p>{product.description}</p>
                    </div>

                    <div className="features">
                        <h3>Features</h3>
                        <ul>
                            {product.features && product.features.split(',').map((f, idx) => (
                                <li key={idx}>{f.trim()}</li>
                            ))}
                        </ul>
                    </div>

                    <a href={product.url} target="_blank" rel="noopener noreferrer" className="buy-btn">
                        Buy on {product.source}
                    </a>
                </div>
            </div>
        </div>
    );
};

export default ProductDetail;
