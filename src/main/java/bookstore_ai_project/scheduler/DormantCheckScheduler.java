package bookstore_ai_project.scheduler;

import bookstore_ai_project.service.LoginService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 휴면상태 자동 체크 스케줄러
 * 매일 새벽 2시에 6개월 이상 미로그인 사용자를 휴면상태로 변경
 */
@Component
public class DormantCheckScheduler {

    @Autowired
    private LoginService loginService;

    /**
     * 매일 새벽 2시에 휴면상태 체크 실행
     * cron 표현식: 초 분 시 일 월 요일
     */
    @Scheduled(cron = "0 0 2 * * *")
    public void checkDormantUsers() {
        System.out.println("=== 휴면상태 자동 체크 시작 ===");

        try {
            loginService.checkAndUpdateDormantUsers();
            System.out.println("=== 휴면상태 자동 체크 완료 ===");
        } catch (Exception e) {
            System.err.println("휴면상태 자동 체크 중 오류 발생: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 테스트용 - 매 10분마다 실행 (개발 중에만 사용)
     * 실제 배포시에는 주석 처리하거나 삭제
     */
    // @Scheduled(fixedRate = 600000) // 10분 = 600,000ms
    public void checkDormantUsersForTest() {
        System.out.println("=== 휴면상태 테스트 체크 시작 ===");

        try {
            loginService.checkAndUpdateDormantUsers();
            System.out.println("=== 휴면상태 테스트 체크 완료 ===");
        } catch (Exception e) {
            System.err.println("휴면상태 테스트 체크 중 오류 발생: " + e.getMessage());
            e.printStackTrace();
        }
    }
}