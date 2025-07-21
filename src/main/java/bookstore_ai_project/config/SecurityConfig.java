package bookstore_ai_project.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Spring Security 보안 설정 클래스
 *
 * 비즈니스 로직: AI 도서 추천 시스템의 보안 정책 설정 (CSRF 비활성화, 폼 로그인 비활성화)
 */
@Configuration
public class SecurityConfig {

    /**
     * Spring Security 필터 체인 설정
     *
     * 비즈니스 로직: AJAX 기반 인증을 위한 보안 설정 (CSRF 비활성화, 모든 경로 허용)
     *
     * @param http HTTP 보안 설정 객체
     * @return 설정된 보안 필터 체인
     * @throws Exception 보안 설정 오류 시
     */
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)  // CSRF 비활성화 (AJAX 로그인용)
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/**").permitAll()   // 모든 경로 허용 (우리가 직접 인증 처리)
                )
                .formLogin(AbstractHttpConfigurer::disable)  // 기본 폼 로그인 완전 비활성화
                .logout(logout -> logout
                        .logoutUrl("/logout")
                        .logoutSuccessHandler((request, response, authentication) -> {
                            response.setStatus(HttpServletResponse.SC_OK); // 리다이렉트 없이 200 OK만 반환
                        })
                        .invalidateHttpSession(true)
                        .deleteCookies("JSESSIONID")
                );

        return http.build();
    }
}