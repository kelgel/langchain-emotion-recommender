package bookstore_ai_project.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.filter.CharacterEncodingFilter;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Spring Web MVC 설정 클래스
 *
 * 비즈니스 로직: UTF-8 인코딩 설정으로 한글 데이터 처리 보장
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    /**
     * UTF-8 문자 인코딩 필터 생성
     *
     * 비즈니스 로직: 전체 요청/응답의 UTF-8 인코딩 강제 설정으로 한글 처리 보장
     *
     * @return UTF-8 인코딩 필터
     */
    @Bean
    public CharacterEncodingFilter characterEncodingFilter() {
        CharacterEncodingFilter filter = new CharacterEncodingFilter();
        filter.setEncoding("UTF-8");
        filter.setForceEncoding(true);
        filter.setForceRequestEncoding(true);
        filter.setForceResponseEncoding(true);
        return filter;
    }
}