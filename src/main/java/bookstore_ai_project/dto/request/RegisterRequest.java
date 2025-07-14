package bookstore_ai_project.dto.request;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Pattern;
import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {

    @NotBlank(message = "이름을 입력해 주세요.")
    private String userName;

    @NotBlank(message = "닉네임을 입력해 주세요.")
    private String userNickname;

    @NotBlank(message = "아이디를 입력해 주세요.")
    @Pattern(regexp = "^[a-z0-9]{6,15}$", message = "아이디는 영문 소문자, 숫자 조합으로 6~15자여야 합니다.")
    private String idForUser;

    @NotBlank(message = "비밀번호를 입력해 주세요.")
    private String userPwd;

    @NotNull(message = "생년월일을 입력해 주세요.")
    private LocalDate userBirth;

    @NotBlank(message = "이메일을 입력해 주세요.")
    @Email(message = "올바른 이메일 형식을 입력해 주세요.")
    private String userEmail;

    @NotBlank(message = "휴대폰 번호를 입력해 주세요.")
    private String userPhoneNumber;

    @NotBlank(message = "주소를 입력해 주세요.")
    private String userAddress;

    @NotBlank(message = "상세주소를 입력해 주세요.")
    private String userAddressDetail;

    @NotBlank(message = "성별을 선택해 주세요.")
    @Pattern(regexp = "^(M|F)$", message = "성별은 M 또는 F여야 합니다.")
    private String userGender;
}