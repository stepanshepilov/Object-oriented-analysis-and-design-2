// package com.example.demo.kolhoz;

// import com.example.demo.domain.model.OrderRequest;
// import com.example.demo.domain.model.ProductRequest;
// import org.springframework.jdbc.core.JdbcTemplate;
// import org.springframework.kafka.core.KafkaTemplate;
// import org.springframework.web.bind.annotation.*;

// import java.util.List;
// import java.util.Map;

// @RestController
// @RequestMapping("/api")
// @CrossOrigin(origins = "http://localhost:5173")
// public class KolkhozProductController {

//     private final JdbcTemplate jdbcTemplate;
//     private final KafkaTemplate<String, String> kafkaTemplate;

//     public KolkhozProductController(JdbcTemplate jdbcTemplate, KafkaTemplate<String, String> kafkaTemplate) {
//         this.jdbcTemplate = jdbcTemplate;
//         this.kafkaTemplate = kafkaTemplate;
//     }

//     @GetMapping("/products")
//     public List<Map<String, Object>> getAllProducts() {
//         return jdbcTemplate.queryForList("SELECT * FROM products");
//     }

//     @PostMapping("/order")
//     public String order(@RequestBody OrderRequest request) {
//         int updated = jdbcTemplate.update(
//                 "UPDATE products SET stock = stock - ? WHERE name = ? AND stock >= ?",
//                 request.quantity(), request.productName(), request.quantity());

//         boolean success = updated > 0;

//         if (success) {
//             kafkaTemplate.send("product-updates", "ЗАКАЗ: " + request.quantity() + " шт. " + request.productName());
//             return "Заказ на " + request.productName() + " оформлен! (через колхоз)";
//         } else {
//             return "Нет в наличии! (через колхоз)";
//         }
//     }

//     @PostMapping("/admin/add")
//     public String addProduct(@RequestBody ProductRequest request) {
//         jdbcTemplate.update(
//                 "INSERT INTO products (name, price, stock) VALUES (?, ?, ?) " +
//                         "ON CONFLICT (name) DO UPDATE SET price = ?, stock = products.stock + ?",
//                 request.name(), request.price(), request.stock(), request.price(), request.stock());
        
//         return "Товар " + request.name() + " добавлен! (через колхоз)";
//     }
// }
