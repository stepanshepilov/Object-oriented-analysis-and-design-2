CREATE TABLE IF NOT EXISTS products (
    name VARCHAR(255) PRIMARY KEY,
    price DOUBLE PRECISION,
    stock INT
);

INSERT INTO products (name, price, stock) 
VALUES ('iPhone 9000 Ultra Hyper Pro Max Plus', 1000.0, 10) 
ON CONFLICT (name) DO NOTHING;

INSERT INTO products (name, price, stock) 
VALUES ('MacBook MMM777 Hyper Pro 1 Tb 1 TB', 2500.0, 7) 
ON CONFLICT (name) DO NOTHING;


INSERT INTO products (name, price, stock) 
VALUES ('Купить Технику Apple онлайн без смс и мас', 100.0, 100) 
ON CONFLICT (name) DO NOTHING;

INSERT INTO products (name, price, stock) 
VALUES ('Грушофон', 100.0, 100) 
ON CONFLICT (name) DO NOTHING;

INSERT INTO products (name, price, stock) 
VALUES ('Партия одобряет', 100000000000.0, 1) 
ON CONFLICT (name) DO NOTHING;
