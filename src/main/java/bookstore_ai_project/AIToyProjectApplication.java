package bookstore_ai_project;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * AI 기반 도서 추천 시스템의 메인 애플리케이션 클래스
 *
 * 비즈니스 로직: Spring Boot 애플리케이션 시작점으로 AI 추천 시스템 전체를 구동
 */
@SpringBootApplication
@EnableScheduling  // 스케줄러 활성화 - 휴면 계정 처리 등 배치 작업용
public class AIToyProjectApplication {

    /**
     * 애플리케이션 메인 메서드 - Spring Boot 컨테이너 시작
     *
     * 비즈니스 로직: 전체 시스템 구동 및 컴포넌트 스캔 실행
     *
     * @param args 명령행 인수
     */
    public static void main(String[] args) {
        SpringApplication.run(AIToyProjectApplication.class, args);
    }

}