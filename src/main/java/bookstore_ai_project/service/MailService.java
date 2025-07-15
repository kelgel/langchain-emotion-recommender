package bookstore_ai_project.service;

import jakarta.mail.internet.MimeMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

@Service
public class MailService {

    @Autowired(required = false)
    private JavaMailSender mailSender;

    @Value("${mail.sender.email}")
    private String senderEmail;

    @Value("${mail.sender.name}")
    private String senderName;

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