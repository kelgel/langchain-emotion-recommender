package bookstore_ai_project.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;
import jakarta.servlet.http.HttpServletResponse;

/**
 * 간소화된 Spring Security 설정
 * 평문 비밀번호 사용으로 암호화 기능 제거
 */
@Configuration
public class SecurityConfig {

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