package com.example.demo.domain.service;

import com.example.demo.domain.repository.ProductRepository;
import com.example.demo.domain.EventPublisher;
import org.springframework.stereotype.Service;

@Service
public class OrderService {
    private final ProductRepository productRepository;
    private final EventPublisher publisher;

    public OrderService(ProductRepository productRepository, EventPublisher publisher) {
        this.productRepository = productRepository;
        this.publisher = publisher;
    }

    public boolean placeOrder(String product, int quantity) {
        if (productRepository.decreaseStock(product, quantity)) {
            publisher.sendEvent("ЗАКАЗ: " + quantity + " шт. " + product);
            return true;
        }
        return false;
    }
}
