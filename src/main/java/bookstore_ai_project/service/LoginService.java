package bookstore_ai_project.service;

import bookstore_ai_project.dto.request.LoginRequest;
import bookstore_ai_project.dto.response.LoginResponse;
import bookstore_ai_project.entity.User;
import bookstore_ai_project.entity.Admin;
import bookstore_ai_project.repository.UserRepository;
import bookstore_ai_project.repository.AdminRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.Optional;

/**
 * 로그인/인증 관리 비즈니스 로직 서비스
 *
 * 비즈니스 로직: 사용자/관리자 로그인 처리, 휴면 계정 관리, 로그인 실패 기록 등
 */
@Service
@Transactional
public class LoginService {

    private static final Logger logger = LoggerFactory.getLogger(LoginService.class);

    /** 사용자 데이터 접근 리포지토리 */
    @Autowired
    private UserRepository userRepository;

    /** 관리자 데이터 접근 리포지토리 */
    @Autowired
    private AdminRepository adminRepository;

    /** 메일 전송 서비스 */
    @Autowired
    private MailService mailService;

    /**
     * 사용자/관리자 로그인 인증 처리
     *
     * 비즈니스 로직: 아이디와 비밀번호 평문 비교, 휴면 상태 확인, 로그인 실패 기록 처리
     *
     * @param loginRequest 로그인 요청 데이터 (username, password)
     * @return 로그인 결과 및 사용자 정보 (LoginResponse)
     */
    public LoginResponse authenticate(LoginRequest loginRequest) {
        try {
            logger.info("=== 로그인 요청 시작 ===");
            logger.info("입력된 아이디: {}", loginRequest.getUsername());
            logger.info("입력된 비밀번호 길이: {}", loginRequest.getPassword() != null ? loginRequest.getPassword().length() : 0);

            // 1. 휴면 상태 체크 및 업데이트 실행
            checkAndUpdateDormantUsers();

            // 2. 사용자 조회
            Optional<User> userOptional = userRepository.findByIdForUser(loginRequest.getUsername());

            if (userOptional.isEmpty()) {
                logger.warn("❌ 사용자를 찾을 수 없음: {}", loginRequest.getUsername());
                return LoginResponse.failure("입력하신 아이디가 존재하지 않습니다.");
            }

            User user = userOptional.get();
            logger.info("✅ 사용자 찾음: {}", user.getIdForUser());
            logger.info("저장된 비밀번호: {}", user.getUserPwd());
            logger.info("사용자 상태: {}", user.getUserStatus());

            // 3. 비밀번호 검증 (평문 비교)
            logger.info("=== 비밀번호 검증 시작 ===");
            logger.info("입력 비밀번호: '{}'", loginRequest.getPassword());
            logger.info("저장된 비밀번호: '{}'", user.getUserPwd());

            // 평문으로 직접 비교
            boolean passwordMatches = loginRequest.getPassword().equals(user.getUserPwd());
            logger.info("비밀번호 일치 여부: {}", passwordMatches);

            if (!passwordMatches) {
                logger.warn("❌ 비밀번호 불일치");
                return LoginResponse.failure("입력하신 정보가 일치하지 않습니다.");
            }

            logger.info("✅ 비밀번호 일치 확인");

            // 4. 사용자 상태 검증
            LoginResponse statusResponse = validateUserStatus(user);
            if (!statusResponse.isSuccess()) {
                logger.warn("❌ 사용자 상태 문제: {}", statusResponse.getMessage());
                return statusResponse;
            }

            // 5. 로그인 성공 - 마지막 로그인 시간 업데이트
            LocalDateTime loginTime = LocalDateTime.now();
            userRepository.updateLastLoginDate(user.getIdForAdmin(), loginTime);

            // 6. 응답 생성
            String redirectUrl = loginRequest.getRedirectUrl() != null ?
                    loginRequest.getRedirectUrl() : "/main";

            logger.info("✅ 로그인 성공: {}", user.getIdForUser());
            return LoginResponse.success(user, redirectUrl);

        } catch (Exception e) {
            logger.error("❌ 로그인 처리 중 오류 발생: {}", e.getMessage());
            e.printStackTrace();
            return LoginResponse.failure("로그인 처리 중 오류가 발생했습니다.");
        }
    }

    /**
     * 사용자 상태 검증
     *
     * 비즈니스 로직: 사용자의 상태(활성, 탈퇴, 비활성, 휴면 등)를 확인하여 로그인 가능 여부를 판단
     *
     * @param user 상태를 검증할 User 엔티티
     * @return 상태에 따른 LoginResponse
     */
    private LoginResponse validateUserStatus(User user) {
        logger.info("=== 사용자 상태 검증: {} ===", user.getUserStatus());

        return switch (user.getUserStatus()) {
            case ACTIVE -> {
                logger.info("✅ 활성 사용자");
                yield LoginResponse.builder().success(true).build();
            }
            case WITHDRAWN -> {
                logger.warn("❌ 탈퇴한 사용자");
                yield LoginResponse.failure("회원정보가 없습니다. 회원가입을 해주세요.");
            }
            case INACTIVE -> {
                logger.warn("❌ 비활성 사용자");
                yield LoginResponse.failure("비활성화 상태입니다. 고객센터로 문의해주세요.");
            }
            case DORMANT -> {
                logger.warn("❌ 휴면 사용자");
                yield LoginResponse.failure("휴면상태입니다. 비밀번호 찾기를 통해 휴면상태를 해제해주세요.");
            }
            default -> {
                logger.warn("❌ 알 수 없는 상태: {}", user.getUserStatus());
                yield LoginResponse.failure("알 수 없는 계정 상태입니다. 고객센터로 문의해주세요.");
            }
        };
    }

    /**
     * 휴면 상태 체크 및 업데이트
     *
     * 비즈니스 로직: 최근 6개월간 로그인 이력이 없는 사용자를 휴면 상태로 일괄 변경
     *
     * @return 없음
     */
    public void checkAndUpdateDormantUsers() {
        try {
            LocalDateTime cutoffDate = LocalDateTime.now().minusMonths(6);
            LocalDateTime updateDate = LocalDateTime.now();

            int updatedCount = userRepository.updateUserStatusToDormant(cutoffDate, updateDate);

            if (updatedCount > 0) {
                logger.info("휴면 상태로 변경된 사용자 수: {}", updatedCount);
            }
        } catch (Exception e) {
            logger.error("휴면 상태 업데이트 중 오류 발생: {}", e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 아이디 찾기
     *
     * 비즈니스 로직: 이름과 이메일로 회원을 찾아 아이디(마스킹 처리)를 반환
     *
     * @param name 회원 이름
     * @param email 회원 이메일
     * @return 아이디(마스킹) 또는 실패 메시지의 LoginResponse
     */
    @Transactional(readOnly = true)
    public LoginResponse findUserId(String name, String email) {
        try {
            logger.info("=== 아이디 찾기 ===");
            logger.info("이름: {}, 이메일: {}", name, email);

            Optional<User> userOptional = userRepository.findByUserEmailAndUserName(email, name);

            if (userOptional.isEmpty()) {
                logger.warn("❌ 일치하는 사용자 없음");
                return LoginResponse.failure("입력하신 정보와 일치하는 회원 정보를 찾을 수 없습니다.");
            }

            User user = userOptional.get();
            logger.info("✅ 사용자 찾음: {}", user.getIdForUser());

            // 탈퇴한 회원은 아이디 찾기 불가
            if (user.getUserStatus() == User.UserStatus.WITHDRAWN) {
                logger.warn("❌ 탈퇴한 회원");
                return LoginResponse.failure("입력하신 정보와 일치하는 회원 정보를 찾을 수 없습니다.");
            }

            // 아이디 일부 마스킹 처리 (보안상)
            String maskedId = maskUserId(user.getIdForUser());
            logger.info("마스킹된 아이디: {}", maskedId);

            return LoginResponse.builder()
                    .success(true)
                    .message("아이디 찾기 성공")
                    .userInfo(LoginResponse.UserInfo.builder()
                            .idForUser(maskedId)
                            .build())
                    .build();

        } catch (Exception e) {
            logger.error("아이디 찾기 중 오류 발생: {}", e.getMessage());
            e.printStackTrace();
            return LoginResponse.failure("아이디 찾기 중 오류가 발생했습니다.");
        }
    }

    /**
     * 비밀번호 찾기 (임시 비밀번호 발급)
     *
     * 비즈니스 로직: 아이디와 이름으로 회원을 찾아 임시 비밀번호를 발급 및 이메일로 전송
     *
     * @param username 회원 아이디
     * @param name 회원 이름
     * @return 처리 결과 메시지의 LoginResponse
     */
    @Transactional
    public LoginResponse findPassword(String username, String name) {
        try {
            logger.info("=== 비밀번호 찾기 ===");
            logger.info("아이디: {}, 이름: {}", username, name);

            Optional<User> userOptional = userRepository.findByIdForUserAndUserName(username, name);

            if (userOptional.isEmpty()) {
                logger.warn("❌ 일치하는 사용자 없음");
                return LoginResponse.failure("입력하신 정보와 일치하는 회원 정보를 찾을 수 없습니다.");
            }

            User user = userOptional.get();
            logger.info("✅ 사용자 찾음: {}", user.getIdForUser());

            // 탈퇴한 회원은 비밀번호 찾기 불가
            if (user.getUserStatus() == User.UserStatus.WITHDRAWN) {
                logger.warn("❌ 탈퇴한 회원");
                return LoginResponse.failure("입력하신 정보와 일치하는 회원 정보를 찾을 수 없습니다.");
            }

            // 휴면 상태인 경우 활성화
            if (user.getUserStatus() == User.UserStatus.DORMANT) {
                user.setUserStatus(User.UserStatus.ACTIVE);
                user.setUpdateDate(LocalDateTime.now());
                userRepository.save(user);
                logger.info("휴면 해제 완료: {}", user.getIdForUser());
            }

            // 임시 비밀번호 생성 및 저장
            String tempPassword = generateTempPassword();
            logger.info("임시 비밀번호 생성: {}", tempPassword);
            user.setUserPwd(tempPassword);
            user.setUpdateDate(LocalDateTime.now());
            userRepository.save(user);
            logger.info("임시 비밀번호 설정 완료: {} -> {}", user.getIdForUser(), tempPassword);

            // 이메일로 임시 비밀번호 발송
            if (user.getUserEmail() != null && !user.getUserEmail().isEmpty()) {
                try {
                    mailService.sendTempPasswordMail(user.getUserEmail(), tempPassword);
                    logger.info("임시 비밀번호 이메일 발송 완료: {}", user.getUserEmail());
                } catch (Exception e) {
                    logger.error("임시 비밀번호 이메일 발송 실패: {}", e.getMessage());
                }
            } else {
                logger.warn("이메일 정보가 없어 임시 비밀번호 메일을 발송하지 못함: {}", user.getIdForUser());
            }

            return LoginResponse.builder()
                    .success(true)
                    .message("임시 비밀번호가 등록된 이메일로 전송되었습니다.")
                    .build();

        } catch (Exception e) {
            logger.error("비밀번호 찾기 중 오류 발생: {}", e.getMessage());
            e.printStackTrace();
            return LoginResponse.failure("비밀번호 찾기 중 오류가 발생했습니다.");
        }
    }

    /**
     * 아이디 마스킹 처리
     *
     * 비즈니스 로직: 아이디 일부를 *로 마스킹하여 반환
     *
     * @param userId 마스킹할 아이디
     * @return 마스킹된 아이디 문자열
     */
    private String maskUserId(String userId) {
        if (userId == null || userId.length() <= 3) {
            return userId;
        }

        int visibleLength = Math.min(3, userId.length() / 2);
        String visiblePart = userId.substring(0, visibleLength);
        String maskedPart = "*".repeat(userId.length() - visibleLength);

        return visiblePart + maskedPart;
    }

    /**
     * 관리자 로그인 처리
     *
     * 비즈니스 로직: 관리자 아이디와 비밀번호를 검증하여 로그인 처리
     *
     * @param loginRequest 관리자 로그인 요청 정보
     * @return 처리 결과 메시지의 LoginResponse
     */
    public LoginResponse authenticateAdmin(LoginRequest loginRequest) {
        try {
            logger.info("=== 관리자 로그인 요청 시작 ===");
            logger.info("입력된 관리자 아이디: {}", loginRequest.getUsername());
            
            // 1. 관리자 조회
            Optional<Admin> adminOptional = adminRepository.findActiveAdminByAdminId(loginRequest.getUsername());
            
            if (adminOptional.isEmpty()) {
                logger.warn("❌ 관리자를 찾을 수 없음: {}", loginRequest.getUsername());
                return LoginResponse.failure("관리자 정보가 존재하지 않습니다.");
            }
            
            Admin admin = adminOptional.get();
            logger.info("✅ 관리자 찾음: {}", admin.getAdminId());
            
            // 2. 비밀번호 검증
            if (!loginRequest.getPassword().equals(admin.getAdminPwd())) {
                logger.warn("❌ 관리자 비밀번호 불일치");
                return LoginResponse.failure("관리자 정보가 일치하지 않습니다.");
            }
            
            logger.info("✅ 관리자 로그인 성공: {}", admin.getAdminId());
            
            // 3. 관리자 로그인 응답 생성
            return LoginResponse.builder()
                    .success(true)
                    .message("관리자 로그인 성공")
                    .redirectUrl("/admin/product-inquiry")
                    .userInfo(LoginResponse.UserInfo.builder()
                            .idForUser(admin.getAdminId())
                            .userName(admin.getAdminName())
                            .build())
                    .build();
                    
        } catch (Exception e) {
            logger.error("❌ 관리자 로그인 처리 중 오류 발생: {}", e.getMessage());
            e.printStackTrace();
            return LoginResponse.failure("관리자 로그인 처리 중 오류가 발생했습니다.");
        }
    }

    /**
     * 임시 비밀번호 생성 (단순화)
     *
     * 비즈니스 로직: 간단한 임시 비밀번호를 생성하여 반환
     *
     * @return 임시 비밀번호 문자열
     */
    private String generateTempPassword() {
        return "temp123!";  // 간단한 임시 비밀번호
    }
}