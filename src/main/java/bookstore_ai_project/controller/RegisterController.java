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

    private final RegisterService registerService;
    private final UserRepository userRepository;

    public RegisterController(RegisterService registerService, UserRepository userRepository) {
        this.registerService = registerService;
        this.userRepository = userRepository;
    }

    @RequestMapping("/register")
    public String register(HttpServletRequest request) {
        // referer 정보를 세션에 저장
        String referer = request.getHeader("Referer");
        if (referer != null && !referer.contains("/register")) {
            request.getSession().setAttribute("registerReferer", referer);
        }
        return "user/register";
    }

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

    @GetMapping("/api/check-joinable")
    @ResponseBody
    public RegisterResponse checkJoinable(
            @RequestParam String userName,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate userBirth
    ) {
        return registerService.checkJoinable(userName, userBirth);
    }

    @GetMapping("/api/check-nickname")
    @ResponseBody
    public Map<String, Boolean> checkNickname(@RequestParam String nickname) {
        boolean exists = userRepository.existsByUserNickname(nickname);
        return Map.of("duplicated", exists);
    }

    @GetMapping("/api/check-id")
    @ResponseBody
    public Map<String, Boolean> checkId(@RequestParam String userId) {
        boolean exists = userRepository.existsByIdForUser(userId);
        return Map.of("duplicated", exists);
    }

    @GetMapping("/api/check-email")
    @ResponseBody
    public Map<String, Boolean> checkEmail(@RequestParam String email) {
        boolean exists = userRepository.existsByUserEmail(email);
        return Map.of("duplicated", exists);
    }
}
