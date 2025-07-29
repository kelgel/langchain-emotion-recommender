package bookstore_ai_project.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

/**
 * AI 채팅 서비스
 * 
 * 비즈니스 로직: Java 서비스에서 Python FastAPI로 HTTP 요청을 보내는 로직
 */
@Service
@Slf4j
public class AIChatService {

    @Value("${ai.service.base-url:http://ai-service:8000}")
    private String pythonServiceUrl;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public AIChatService() {
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * 사용자 메시지를 Python AI 서비스로 전달
     */
    public Map<String, Object> sendMessageToAI(String userMessage) {
        try {
            // 요청 바디 구성
            Map<String, String> requestBody = Map.of("message", userMessage);

            // HTTP 헤더 설정
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // HTTP 요청 엔티티 생성
            HttpEntity<Map<String, String>> requestEntity = new HttpEntity<>(requestBody, headers);

            // Python FastAPI 서비스 호출
            String apiUrl = pythonServiceUrl + "/api/chat";

            ResponseEntity<String> response = restTemplate.exchange(
                apiUrl,
                HttpMethod.POST,
                requestEntity,
                String.class
            );

            if (response.getStatusCode() == HttpStatus.OK) {
                // JSON 응답을 Map으로 변환
                Map<String, Object> responseMap = objectMapper.readValue(
                    response.getBody(), 
                    Map.class
                );
                
                return Map.of(
                    "success", true,
                    "response", responseMap.get("response")
                );
            } else {
                return Map.of(
                    "success", false,
                    "error", "AI 서비스 오류가 발생했습니다."
                );
            }

        } catch (Exception e) {
            return Map.of(
                "success", false,
                "error", "AI 서비스 연결에 실패했습니다."
            );
        }
    }

}