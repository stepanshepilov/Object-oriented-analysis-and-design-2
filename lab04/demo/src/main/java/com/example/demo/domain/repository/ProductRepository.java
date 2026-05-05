package com.example.demo.domain.repository;

import java.util.List;
import java.util.Map;

public interface ProductRepository {
    boolean decreaseStock(String name, int quantity);
    void addProduct(String name, Double price, int stock);
    List<Map<String, Object>> findAll();
}
