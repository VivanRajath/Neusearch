-- Initialize database schema and triggers for product sync

-- Create products table if not exists (should be handled by SQLAlchemy, but included for completeness)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    url TEXT,
    title TEXT,
    price VARCHAR(50),
    description TEXT,
    features TEXT,
    images TEXT,
    category VARCHAR(200),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP
);

-- Create index on synced_at for efficient querying of unsynced products
CREATE INDEX IF NOT EXISTS idx_products_synced_at ON products(synced_at);
CREATE INDEX IF NOT EXISTS idx_products_updated_at ON products(updated_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on product updates
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Create notification function for real-time sync (advanced feature)
CREATE OR REPLACE FUNCTION notify_product_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('product_changes', json_build_object(
        'operation', TG_OP,
        'id', NEW.id,
        'title', NEW.title
    )::text);
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Optional: Create trigger for notifications
DROP TRIGGER IF EXISTS product_change_notification ON products;
CREATE TRIGGER product_change_notification
    AFTER INSERT OR UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION notify_product_change();

-- Grant necessary permissions (adjust user as needed)
GRANT ALL PRIVILEGES ON TABLE products TO myapp_user;
GRANT USAGE, SELECT ON SEQUENCE products_id_seq TO myapp_user;
