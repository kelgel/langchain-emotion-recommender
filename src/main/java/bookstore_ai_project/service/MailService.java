package bookstore_ai_project.service;

import jakarta.mail.internet.MimeMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

/**
 * 메일 전송 비즈니스 로직 서비스
 *
 * 비즈니스 로직: 임시 비밀번호 등 시스템 내 메일 전송 기능 제공
 */
@Service
public class MailService {

    /** Spring 메일 전송 인터페이스 */
    @Autowired(required = false)
    private JavaMailSender mailSender;

    /** 발신자 이메일 주소 */
    @Value("${mail.sender.email}")
    private String senderEmail;

    /** 발신자 이름 */
    @Value("${mail.sender.name}")
    private String senderName;

    /**
     * 임시 비밀번호 안내 메일 전송
     *
     * 비즈니스 로직: 비밀번호 찾기 시 생성된 임시 비밀번호를 사용자 이메일로 전송
     *
     * @param to 수신자 이메일 주소
     * @param tempPassword 전송할 임시 비밀번호
     * @throws Exception 메일 전송 실패 시
     */
    public void sendTempPasswordMail(String to, String tempPassword) throws Exception {
        if (mailSender == null) {
            System.out.println("[MAIL] 메일 서비스가 비활성화되어 있습니다. 임시 비밀번호: " + tempPassword);
            return;
        }
        
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, false, "UTF-8");

        helper.setTo(to);
        helper.setSubject("[책크인] 임시 비밀번호 안내");
        helper.setFrom(senderEmail, senderName);
        helper.setText(
                "안녕하세요. 책크인입니다.\n\n" +
                "임시 비밀번호: " + tempPassword + "\n\n" +
                "로그인 후 회원정보를 꼭 수정해주세요."
        );

        mailSender.send(message);
    }
}