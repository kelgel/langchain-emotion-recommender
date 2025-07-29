package bookstore_ai_project.controller;

import bookstore_ai_project.service.AIChatService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * AI 채팅 컨트롤러
 */
@RestController
@RequestMapping("/api/chat")
public class AIChatController {

    @Autowired
    private AIChatService aiChatService;

    /**
     * 채팅 메시지 전송
     */
    @PostMapping("/message")
    public ResponseEntity<Map<String, Object>> sendMessage(@RequestBody Map<String, String> request) {
        String userMessage = request.get("message");
        
        if (userMessage == null || userMessage.trim().isEmpty()) {
            return ResponseEntity.badRequest()
                .body(Map.of("success", false, "error", "메시지가 비어있습니다."));
        }

        Map<String, Object> aiResponse = aiChatService.sendMessageToAI(userMessage);
        return ResponseEntity.ok(aiResponse);
    }
}