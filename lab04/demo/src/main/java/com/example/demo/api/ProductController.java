package com.example.demo.api;

import com.example.demo.domain.model.OrderRequest;
import com.example.demo.domain.model.ProductRequest;
import com.example.demo.domain.repository.ProductRepository;
import com.example.demo.domain.service.OrderService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:5173")
public class ProductController {

    private final OrderService orderService;
    private final ProductRepository repository;

    public ProductController(OrderService orderService, ProductRepository repository) {
        this.orderService = orderService;
        this.repository = repository;
    }

    @GetMapping("/products")
    public List<Map<String, Object>> getAllProducts() {
        return repository.findAll();
    }

    @PostMapping("/order")
    public String order(@RequestBody OrderRequest request) {
        boolean success = orderService.placeOrder(request.productName(), request.quantity());
        return success ? "Заказ на " + request.productName() + " оформлен!" : "Нет в наличии!";
    }

    @PostMapping("/admin/add")
    public String addProduct(@RequestBody ProductRequest request) {
        repository.addProduct(request.name(), request.price(), request.stock());
        return "Товар " + request.name() + " добавлен!";
    }
}
