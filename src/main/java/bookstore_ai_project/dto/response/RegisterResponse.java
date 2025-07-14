package bookstore_ai_project.dto.response;

public class RegisterResponse {
    private boolean joinable;
    private String message;

    public RegisterResponse(boolean joinable, String message) {
        this.joinable = joinable;
        this.message = message;
    }

    public boolean isJoinable() {
        return joinable;
    }

    public void setJoinable(boolean joinable) {
        this.joinable = joinable;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
