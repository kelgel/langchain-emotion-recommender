package bookstore_ai_project.service;

import bookstore_ai_project.repository.UserRepository;
import bookstore_ai_project.dto.response.RegisterResponse;
import bookstore_ai_project.dto.request.RegisterRequest;
import bookstore_ai_project.entity.User;
import org.springframework.stereotype.Service;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 회원가입 비즈니스 로직 서비스
 *
 * 비즈니스 로직: 신규 회원 가입 처리, 중복 검증, 사용자 데이터 생성 등
 */
@Service
public class RegisterService {
    /** 사용자 데이터 접근 리포지토리 */
    private final UserRepository userRepository;

    /**
     * RegisterService 생성자
     *
     * @param userRepository 사용자 데이터 리포지토리
     */
    public RegisterService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * 신규 회원 가입 처리
     *
     * 비즈니스 로직: 중복 검증(아이디/닉네임/이메일) 후 신규 사용자 데이터 생성 및 저장
     *
     * @param registerRequest 회원가입 요청 데이터 (아이디, 비밀번호, 개인정보 등)
     * @throws RuntimeException 중복된 아이디/닉네임/이메일 사용 시
     */
    public void registerUser(RegisterRequest registerRequest) {
        // 중복 검증
        if (userRepository.existsByIdForUser(registerRequest.getIdForUser())) {
            throw new RuntimeException("이미 사용중인 아이디입니다.");
        }
        
        if (userRepository.existsByUserNickname(registerRequest.getUserNickname())) {
            throw new RuntimeException("이미 사용중인 닉네임입니다.");
        }
        
        if (userRepository.existsByUserEmail(registerRequest.getUserEmail())) {
            throw new RuntimeException("이미 사용중인 이메일입니다.");
        }

        // User 엔티티 생성
        User user = new User();
        user.setIdForUser(registerRequest.getIdForUser());
        user.setUserPwd(registerRequest.getUserPwd()); // 실제로는 암호화 필요
        user.setUserName(registerRequest.getUserName());
        user.setUserNickname(registerRequest.getUserNickname());
        user.setUserBirth(registerRequest.getUserBirth());
        user.setUserGender(registerRequest.getUserGender().equals("M") ? User.Gender.MALE : User.Gender.FEMALE);
        user.setUserEmail(registerRequest.getUserEmail());
        user.setUserPhoneNumber(registerRequest.getUserPhoneNumber());
        user.setUserAddress(registerRequest.getUserAddress());
        user.setUserAddressDetail(registerRequest.getUserAddressDetail());
        
        // 기본값 설정
        user.setUserGradeId("BZ"); // 기본 등급
        user.setUserStatus(User.UserStatus.ACTIVE);
        user.setRegDate(LocalDateTime.now());
        user.setUpdateDate(LocalDateTime.now());
        
        // 순차적으로 증가하는 관리자 ID 생성 (U00001, U00002, ...)
        user.setIdForAdmin(generateNextIdForAdmin());
        
        // DB에 저장
        userRepository.save(user);
    }

    /**
     * 다음 관리자 ID 생성
     *
     * 비즈니스 로직: 기존 관리자 ID 중 최대값을 조회하여 순차적으로 증가시킨 새로운 ID 생성
     *
     * @return 새로 생성된 관리자 ID (U00001 형식)
     */
    private String generateNextIdForAdmin() {
        // 최대 ID 조회
        String maxId = userRepository.findMaxIdForAdmin().orElse("U00000");
        
        // 숫자 부분 추출 (U00001 -> 1)
        String numberPart = maxId.substring(1);
        int nextNumber = Integer.parseInt(numberPart) + 1;
        
        // 5자리 숫자로 포맷팅 (1 -> 00001)
        return String.format("U%05d", nextNumber);
    }

    /**
     * 회원가입 가능 여부 확인
     *
     * 비즈니스 로직: 이름과 생년월일로 기존 회원 조회하여 상태별 가입 가능 여부 판단
     *
     * @param userName 사용자 이름
     * @param userBirth 사용자 생년월일
     * @return 가입 가능 여부 및 메시지 (RegisterResponse)
     */
    public RegisterResponse checkJoinable(String userName, LocalDate userBirth) {
        return userRepository.findByUserNameAndUserBirth(userName, userBirth)
                .map(user -> {
                    // 디버깅 로그 (나중에 제거 가능)
                    System.out.println("=== 가입확인 ===");
                    System.out.println("찾은 사용자: " + user.getUserName());
                    System.out.println("사용자 상태: " + user.getUserStatus());

                    // Enum 직접 비교 (더 안전함)
                    User.UserStatus status = user.getUserStatus();

                    switch (status) {
                        case ACTIVE:
                        case INACTIVE:
                            System.out.println("→ 이미 가입된 회원");
                            return new RegisterResponse(false, "이미 가입된 회원입니다.");

                        case DORMANT:
                            System.out.println("→ 휴면상태 회원");
                            return new RegisterResponse(false, "휴면상태입니다. 비밀번호 찾기를 통해 휴면상태를 해제해주세요.");

                        case WITHDRAWN:
                            System.out.println("→ 탈퇴한 회원 - 재가입 가능");
                            return new RegisterResponse(true, "회원가입이 가능합니다.");

                        default:
                            System.out.println("→ 알 수 없는 상태 - 가입 가능");
                            return new RegisterResponse(true, "회원가입이 가능합니다.");
                    }
                })
                .orElse(new RegisterResponse(true, "회원가입이 가능합니다."));
    }
}