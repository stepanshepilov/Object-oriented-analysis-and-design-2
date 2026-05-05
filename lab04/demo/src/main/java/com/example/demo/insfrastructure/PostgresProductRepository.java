package com.example.demo.insfrastructure;

import com.example.demo.domain.repository.ProductRepository;
import org.springframework.context.annotation.Primary;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
@Primary
public class PostgresProductRepository implements ProductRepository {
    private final JdbcTemplate jdbcTemplate;

    public PostgresProductRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public boolean decreaseStock(String name, int quantity) {
        int updated = jdbcTemplate.update(
            "UPDATE products SET stock = stock - ? WHERE name = ? AND stock >= ?", 
            quantity, name, quantity);
        return updated > 0;
    }

    @Override
    public void addProduct(String name, Double price, int stock) {
        jdbcTemplate.update(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?) " +
            "ON CONFLICT (name) DO UPDATE SET price = ?, stock = products.stock + ?",
            name, price, stock, price, stock);
    }

    @Override
    public List<Map<String, Object>> findAll() {
        return jdbcTemplate.queryForList("SELECT * FROM products");
    }
}
