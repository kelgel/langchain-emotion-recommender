package bookstore_ai_project.dto.request;

import lombok.Data;

@Data
public class UserUpdateRequest {
    private String userName;
    private String userNickname;
    private String userPwd;
    private String userEmailId;
    private String userEmailDomain;
    private String userPhone1;
    private String userPhone2;
    private String userPhone3;
    private String userAddress;
    private String userAddressDetail;
} 