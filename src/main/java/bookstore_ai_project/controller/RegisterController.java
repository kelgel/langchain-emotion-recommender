package bookstore_ai_project.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import bookstore_ai_project.dto.response.RegisterResponse;
import bookstore_ai_project.dto.request.RegisterRequest;
import bookstore_ai_project.service.RegisterService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;
import jakarta.servlet.http.HttpServletRequest;
import java.time.LocalDate;
import java.util.Map;
import bookstore_ai_project.repository.UserRepository;

@Controller
@RequestMapping("")
public class RegisterController {
    /** 회원가입 비즈니스 로직 서비스 */
    private final RegisterService registerService;
    /** 사용자 데이터 접근 리포지토리 */
    private final UserRepository userRepository;

    public RegisterController(RegisterService registerService, UserRepository userRepository) {
        this.registerService = registerService;
        this.userRepository = userRepository;
    }

    /**
     * 회원가입 페이지 진입
     *
     * 비즈니스 로직: 회원가입 화면 진입 시 referer 정보를 세션에 저장
     *
     * @param request HTTP 요청 객체
     * @return 회원가입 뷰 이름
     */
    @RequestMapping("/register")
    public String register(HttpServletRequest request) {
        // referer 정보를 세션에 저장
        String referer = request.getHeader("Referer");
        if (referer != null && !referer.contains("/register")) {
            request.getSession().setAttribute("registerReferer", referer);
        }
        return "user/register";
    }

    /**
     * 회원가입 처리 API
     *
     * 비즈니스 로직: 회원가입 요청을 받아 회원 정보를 저장
     *
     * @param registerRequest 회원가입 요청 DTO
     * @return 처리 결과(success, message)
     */
    @PostMapping("/api/register")
    @ResponseBody
    public Map<String, Object> registerUser(@RequestBody RegisterRequest registerRequest) {
        try {
            registerService.registerUser(registerRequest);
            return Map.of("success", true, "message", "회원가입이 완료되었습니다.");
        } catch (Exception e) {
            return Map.of("success", false, "message", e.getMessage());
        }
    }

    /**
     * 회원가입 가능 여부 확인 API
     *
     * 비즈니스 로직: 이름과 생년월일로 회원가입 가능 여부를 반환
     *
     * @param userName 사용자 이름
     * @param userBirth 생년월일
     * @return 가입 가능 여부 및 메시지
     */
    @GetMapping("/api/check-joinable")
    @ResponseBody
    public RegisterResponse checkJoinable(
            @RequestParam String userName,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate userBirth
    ) {
        return registerService.checkJoinable(userName, userBirth);
    }

    /**
     * 닉네임 중복 체크 API
     *
     * 비즈니스 로직: 닉네임 중복 여부 반환
     *
     * @param nickname 닉네임
     * @return 중복 여부(duplicated)
     */
    @GetMapping("/api/check-nickname")
    @ResponseBody
    public Map<String, Boolean> checkNickname(@RequestParam String nickname) {
        boolean exists = userRepository.existsByUserNickname(nickname);
        return Map.of("duplicated", exists);
    }

    /**
     * 아이디 중복 체크 API
     *
     * 비즈니스 로직: 아이디 중복 여부 반환
     *
     * @param userId 사용자 아이디
     * @return 중복 여부(duplicated)
     */
    @GetMapping("/api/check-id")
    @ResponseBody
    public Map<String, Boolean> checkId(@RequestParam String userId) {
        boolean exists = userRepository.existsByIdForUser(userId);
        return Map.of("duplicated", exists);
    }

    /**
     * 이메일 중복 체크 API
     *
     * 비즈니스 로직: 이메일 중복 여부 반환
     *
     * @param email 이메일
     * @return 중복 여부(duplicated)
     */
    @GetMapping("/api/check-email")
    @ResponseBody
    public Map<String, Boolean> checkEmail(@RequestParam String email) {
        boolean exists = userRepository.existsByUserEmail(email);
        return Map.of("duplicated", exists);
    }
}
