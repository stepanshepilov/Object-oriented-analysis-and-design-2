package com.example.demo.insfrastructure;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class OrderWorker {

    @KafkaListener(topics = "product-updates", groupId = "order_group")
    public void listen(String message) {
        System.out.println("**************************************************");
        System.out.println("--- [KAFKA CONSUMER] АСИНХРОННАЯ ОБРАБОТКА ---");
        System.out.println("--- Получено событие: " + message);
        System.out.println("--- Выполняю логирование/отправку уведомления... ---");
        System.out.println("**************************************************");
    }
}
