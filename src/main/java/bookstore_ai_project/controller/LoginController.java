package bookstore_ai_project.controller;

import bookstore_ai_project.dto.request.LoginRequest;
import bookstore_ai_project.dto.response.LoginResponse;
import bookstore_ai_project.service.LoginService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpSession;
import jakarta.servlet.http.HttpServletRequest;

@Controller
@RequestMapping("")
public class LoginController {

    /** 로그인 비즈니스 로직 서비스 */
    @Autowired
    private LoginService loginService;

    /**
     * 로그인 페이지 표시
     *
     * 비즈니스 로직: 로그인 화면을 반환
     *
     * @return 로그인 뷰 이름
     */
    @GetMapping("/login")
    public String loginPage() {
        return "user/login";
    }

    /**
     * 로그인 처리
     *
     * 비즈니스 로직: 아이디, 비밀번호로 로그인 시도 및 세션 저장
     *
     * @param username 사용자 아이디
     * @param password 비밀번호
     * @param redirectUrl 로그인 후 이동할 URL
     * @param session HTTP 세션
     * @return 로그인 결과(LoginResponse)
     */
    @PostMapping("/login")
    @ResponseBody
    public ResponseEntity<LoginResponse> login(@RequestParam("username") String username,
                                               @RequestParam("password") String password,
                                               @RequestParam(value = "redirectUrl", required = false) String redirectUrl,
                                               HttpSession session) {
        try {
            System.out.println("=== 로그인 컨트롤러 진입 ===");
            System.out.println("아이디: " + username);
            System.out.println("비밀번호: " + password);
            System.out.println("리다이렉트 URL: " + redirectUrl);

            // LoginRequest 생성
            LoginRequest loginRequest = new LoginRequest();
            loginRequest.setUsername(username);
            loginRequest.setPassword(password);
            loginRequest.setRedirectUrl(redirectUrl);

            // 로그인 검증 처리 - 먼저 관리자 로그인 시도
            LoginResponse response = loginService.authenticateAdmin(loginRequest);
            boolean isAdmin = response.isSuccess();
            
            // 관리자 로그인 실패 시 일반 사용자 로그인 시도
            if (!response.isSuccess()) {
                response = loginService.authenticate(loginRequest);
            }

            if (response.isSuccess()) {
                // 세션에 사용자 정보 저장
                session.setAttribute("user", response.getUserInfo());
                session.setAttribute("isLoggedIn", true);
                session.setAttribute("isAdmin", isAdmin); // 관리자 여부 저장

                // 세션 만료 시간 설정 (30분)
                session.setMaxInactiveInterval(30 * 60);

                System.out.println("로그인 성공: " + response.getUserInfo().getIdForUser());
                return ResponseEntity.ok(response);
            } else {
                System.out.println("로그인 실패: " + response.getMessage());
                return ResponseEntity.ok(response); // 200으로 반환하고 success 필드로 구분
            }

        } catch (Exception e) {
            System.err.println("로그인 처리 중 예외 발생: " + e.getMessage());
            e.printStackTrace();

            LoginResponse errorResponse = LoginResponse.failure("로그인 처리 중 오류가 발생했습니다.");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * 아이디 찾기 처리
     *
     * 비즈니스 로직: 이름, 이메일로 아이디 찾기
     *
     * @param name 사용자 이름
     * @param email 사용자 이메일
     * @return 결과(LoginResponse)
     */
    @PostMapping("/findId")
    @ResponseBody
    public ResponseEntity<LoginResponse> findId(@RequestParam String name,
                                                @RequestParam String email) {
        try {
            LoginResponse response = loginService.findUserId(name, email);

            if (response.isSuccess()) {
                System.out.println("아이디 찾기 성공: " + name + " / " + email);
                return ResponseEntity.ok(response);
            } else {
                System.out.println("아이디 찾기 실패: " + response.getMessage());
                return ResponseEntity.ok(response); // 200으로 반환
            }

        } catch (Exception e) {
            System.err.println("아이디 찾기 중 예외 발생: " + e.getMessage());
            e.printStackTrace();

            LoginResponse errorResponse = LoginResponse.failure("아이디 찾기 중 오류가 발생했습니다.");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * 비밀번호 찾기 처리
     *
     * 비즈니스 로직: 아이디, 이름으로 비밀번호 찾기
     *
     * @param username 사용자 아이디
     * @param name 사용자 이름
     * @return 결과(LoginResponse)
     */
    @PostMapping("/findPassword")
    @ResponseBody
    public ResponseEntity<LoginResponse> findPassword(@RequestParam String username,
                                                      @RequestParam String name) {
        try {
            LoginResponse response = loginService.findPassword(username, name);

            if (response.isSuccess()) {
                System.out.println("비밀번호 찾기 성공: " + username + " / " + name);
                return ResponseEntity.ok(response);
            } else {
                System.out.println("비밀번호 찾기 실패: " + response.getMessage());
                return ResponseEntity.ok(response); // 200으로 반환
            }

        } catch (Exception e) {
            System.err.println("비밀번호 찾기 중 예외 발생: " + e.getMessage());
            e.printStackTrace();

            LoginResponse errorResponse = LoginResponse.failure("비밀번호 찾기 중 오류가 발생했습니다.");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * 로그아웃 처리
     *
     * 비즈니스 로직: 세션 무효화 및 리다이렉트
     *
     * @param session HTTP 세션
     * @param request HTTP 요청 객체
     * @return 리다이렉트 경로
     */
    @PostMapping("/logout")
    public String logout(HttpSession session, HttpServletRequest request) {
        try {
            String userId = null;
            Object user = session.getAttribute("user");
            if (user != null && user instanceof LoginResponse.UserInfo) {
                userId = ((LoginResponse.UserInfo) user).getIdForUser();
            }

            // 세션 무효화
            session.invalidate();

            System.out.println("로그아웃 완료: " + (userId != null ? userId : "알 수 없는 사용자"));
            
            // 🔒 로그인 필수 페이지에서 로그아웃하면 메인페이지로, 아니면 현재 페이지 유지
            String referer = request.getHeader("Referer");
            if (referer != null && isLoginRequiredPage(referer)) {
                return "redirect:/main";
            } else {
                return referer != null ? "redirect:" + referer : "redirect:/main";
            }

        } catch (Exception e) {
            System.err.println("로그아웃 처리 중 예외 발생: " + e.getMessage());
            e.printStackTrace();
            return "redirect:/main";
        }
    }
    
    /**
     * 로그인이 필요한 페이지인지 확인
     */
    private boolean isLoginRequiredPage(String referer) {
        // 로그인 필수 페이지 URL 패턴들 (실제 구현된 경로만)
        String[] loginRequiredPaths = {
            "/mypage",          // 마이페이지 (실제 경로)
            "/cart",            // 장바구니
            "/order"            // 주문페이지 (order/summary 포함)
        };
        
        for (String path : loginRequiredPaths) {
            if (referer.contains(path)) {
                return true;
            }
        }
        return false;
    }

    /**
     * GET 방식 로그아웃 (헤더 링크용)
     *
     * 비즈니스 로직: GET 요청으로 로그아웃 처리
     *
     * @param session HTTP 세션
     * @param request HTTP 요청 객체
     * @return 리다이렉트 경로
     */
    @GetMapping("/logout")
    public String logoutGet(HttpSession session, HttpServletRequest request) {
        return logout(session, request);
    }

    /**
     * 로그인 상태 확인 API (AJAX용)
     *
     * 비즈니스 로직: 세션에 저장된 로그인 상태를 반환
     *
     * @param session HTTP 세션
     * @return 로그인 상태(LoginResponse)
     */
    @GetMapping("/api/auth/status")
    @ResponseBody
    public ResponseEntity<LoginResponse> checkAuthStatus(HttpSession session) {
        try {
            Object user = session.getAttribute("user");
            Boolean isLoggedIn = (Boolean) session.getAttribute("isLoggedIn");

            if (user != null && isLoggedIn != null && isLoggedIn) {
                LoginResponse response = LoginResponse.builder()
                        .success(true)
                        .message("로그인 상태")
                        .userInfo((LoginResponse.UserInfo) user)
                        .build();
                return ResponseEntity.ok(response);
            } else {
                LoginResponse response = LoginResponse.failure("로그인되지 않음");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }

        } catch (Exception e) {
            System.err.println("로그인 상태 확인 중 예외 발생: " + e.getMessage());
            e.printStackTrace();

            LoginResponse errorResponse = LoginResponse.failure("상태 확인 중 오류가 발생했습니다.");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * 비밀번호 확인(회원정보 수정 전)
     *
     * 비즈니스 로직: 입력한 비밀번호가 실제 비밀번호와 일치하는지 확인
     *
     * @param body password(비밀번호)
     * @param session HTTP 세션
     * @return 성공 여부 및 메시지
     */
    @PostMapping("/api/user/check-password")
    @ResponseBody
    public ResponseEntity<?> checkPassword(@RequestBody java.util.Map<String, String> body, HttpSession session) {
        try {
            Object userObj = session.getAttribute("user");
            if (userObj == null || !(userObj instanceof LoginResponse.UserInfo userInfo)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(java.util.Map.of("success", false, "message", "로그인이 필요합니다."));
            }
            String userId = userInfo.getIdForUser();
            String inputPassword = body.get("password");
            if (inputPassword == null || inputPassword.isBlank()) {
                return ResponseEntity.ok(java.util.Map.of("success", false, "message", "비밀번호를 입력하세요."));
            }
            // 실제 비밀번호 검증
            LoginRequest req = new LoginRequest();
            req.setUsername(userId);
            req.setPassword(inputPassword);
            LoginResponse resp = loginService.authenticate(req);
            if (resp.isSuccess()) {
                return ResponseEntity.ok(java.util.Map.of("success", true));
            } else {
                return ResponseEntity.ok(java.util.Map.of("success", false, "message", "비밀번호가 일치하지 않습니다."));
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(java.util.Map.of("success", false, "message", "서버 오류가 발생했습니다."));
        }
    }
}