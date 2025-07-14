package bookstore_ai_project.dto.response;

import bookstore_ai_project.entity.User;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.io.Serial;
import java.io.Serializable;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LoginResponse {

    private boolean success;
    private String message;
    private String redirectUrl;
    private UserInfo userInfo;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class UserInfo implements Serializable {
        @Serial
        private static final long serialVersionUID = 1L;
        private String idForAdmin;
        private String idForUser;
        private String userName;
        private String userNickname;
        private String userEmail;
        private String userGradeId;
        private User.UserStatus userStatus;
        private String userPhoneNumber;
        private String userAddress;
        private String userAddressDetail;

        public static UserInfo from(User user) {
            return UserInfo.builder()
                    .idForAdmin(user.getIdForAdmin())
                    .idForUser(user.getIdForUser())
                    .userName(user.getUserName())
                    .userNickname(user.getUserNickname())
                    .userEmail(user.getUserEmail())
                    .userGradeId(user.getUserGradeId())
                    .userStatus(user.getUserStatus())
                    .userPhoneNumber(user.getUserPhoneNumber())
                    .userAddress(user.getUserAddress())
                    .userAddressDetail(user.getUserAddressDetail())
                    .build();
        }
    }

    // 성공 응답 생성
    public static LoginResponse success(User user, String redirectUrl) {
        return LoginResponse.builder()
                .success(true)
                .message("로그인 성공")
                .redirectUrl(redirectUrl)
                .userInfo(UserInfo.from(user))
                .build();
    }

    // 실패 응답 생성
    public static LoginResponse failure(String message) {
        return LoginResponse.builder()
                .success(false)
                .message(message)
                .redirectUrl(null)
                .userInfo(null)
                .build();
    }
}