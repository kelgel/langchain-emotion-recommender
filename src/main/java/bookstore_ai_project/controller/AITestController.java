package bookstore_ai_project.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/test")
@Slf4j
public class AITestController {

    @GetMapping("/environment")
    public ResponseEntity<String> testEnvironment() {
        StringBuilder result = new StringBuilder();
        result.append("🔧 환경 변수 확인:\n\n");

        // Java 환경 확인
        result.append("Java 정보:\n");
        result.append("- Java Version: ").append(System.getProperty("java.version")).append("\n");
        result.append("- Working Directory: ").append(System.getProperty("user.dir")).append("\n");
        result.append("- OPENAI_API_KEY: ").append(
                System.getenv("OPENAI_API_KEY") != null ? "✅ 설정됨" : "❌ 없음"
        ).append("\n\n");

        // 환경별 Python 파일 경로 확인
        result.append("Python 파일 확인:\n");

        // Docker 환경 확인
        java.io.File dockerPath = new java.io.File("/app/ai-service/main.py");
        result.append("- Docker 경로 (/app/ai-service/main.py): ")
                .append(dockerPath.exists() ? "✅ 있음" : "❌ 없음").append("\n");

        // 로컬 환경 확인
        java.io.File localPath = new java.io.File("ai-service/main.py");
        result.append("- 로컬 경로 (ai-service/main.py): ")
                .append(localPath.exists() ? "✅ 있음" : "❌ 없음").append("\n");

        // 절대 경로 확인
        String workingDir = System.getProperty("user.dir");
        java.io.File absolutePath = new java.io.File(workingDir + "/ai-service/main.py");
        result.append("- 절대 경로: ").append(absolutePath.getAbsolutePath()).append("\n");
        result.append("- 절대 경로 존재: ").append(absolutePath.exists() ? "✅ 있음" : "❌ 없음").append("\n");

        if (absolutePath.exists()) {
            result.append("- 파일 크기: ").append(absolutePath.length()).append(" bytes\n");
        }

        return ResponseEntity.ok(result.toString());
    }

    @GetMapping("/python")
    public ResponseEntity<String> testPython() {
        try {
            log.info("Python 스크립트 테스트 시작");

            // 환경별 Python 실행 파일 경로 결정
            String pythonPath;
            String pythonCommand;

            java.io.File dockerPath = new java.io.File("/app/ai-service/main.py");
            java.io.File localPath = new java.io.File("ai-service/main.py");

            if (dockerPath.exists()) {
                pythonPath = "/app/ai-service/main.py";
                pythonCommand = "/app/ai_venv/bin/python";  // 가상환경의 Python 사용
                log.info("Docker 환경에서 실행 (가상환경)");
            } else if (localPath.exists()) {
                pythonPath = "ai-service/main.py";
                pythonCommand = "python";   // 로컬에서는 시스템 Python 사용
                log.info("로컬 환경에서 실행");
            } else {
                return ResponseEntity.ok(
                        "❌ Python 파일을 찾을 수 없습니다.\n\n" +
                                "확인된 경로:\n" +
                                "- Docker: /app/ai-service/main.py (존재하지 않음)\n" +
                                "- 로컬: ai-service/main.py (존재하지 않음)\n\n" +
                                "현재 작업 디렉토리: " + System.getProperty("user.dir")
                );
            }

            // Python 스크립트 실행
            ProcessBuilder pb = new ProcessBuilder(pythonCommand, pythonPath, "책 추천해줘");

            // 환경변수 설정
            String apiKey = System.getenv("OPENAI_API_KEY");
            if (apiKey != null) {
                pb.environment().put("OPENAI_API_KEY", apiKey);
            }

            // 가상환경 환경변수 설정 (Docker에서만)
            if (dockerPath.exists()) {
                pb.environment().put("VIRTUAL_ENV", "/app/ai_venv");
                pb.environment().put("PATH", "/app/ai_venv/bin:" + System.getenv("PATH"));
            }

            // UTF-8 인코딩 환경변수 설정
            pb.environment().put("PYTHONIOENCODING", "utf-8");
            pb.environment().put("LC_ALL", "C.UTF-8");
            pb.environment().put("LANG", "C.UTF-8");

            Process process = pb.start();

            // 타임아웃 설정 (15초)
            boolean finished = process.waitFor(15, TimeUnit.SECONDS);

            if (!finished) {
                process.destroyForcibly();
                return ResponseEntity.ok("❌ Python 스크립트 타임아웃");
            }

            // 결과 읽기
            StringBuilder result = new StringBuilder();
            StringBuilder errorOutput = new StringBuilder();

            // 표준 출력 읽기
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                result.append(reader.lines().collect(Collectors.joining("\n")));
            }

            // 에러 출력 읽기
            try (BufferedReader errorReader = new BufferedReader(
                    new InputStreamReader(process.getErrorStream(), StandardCharsets.UTF_8))) {
                errorOutput.append(errorReader.lines().collect(Collectors.joining("\n")));
            }

            log.info("Python 스크립트 실행 결과: {}", result.toString());
            if (errorOutput.length() > 0) {
                log.info("Python 에러 출력: {}", errorOutput.toString());
            }

            StringBuilder response = new StringBuilder();
            response.append("✅ Python 호출 성공!\n\n");
            response.append("🔧 실행 정보:\n");
            response.append("- 사용된 명령어: ").append(pythonCommand).append("\n");
            response.append("- 사용된 경로: ").append(pythonPath).append("\n");
            response.append("- Exit Code: ").append(process.exitValue()).append("\n\n");

            response.append("📄 Python 실행 결과:\n");
            response.append(result.toString());

            if (errorOutput.length() > 0) {
                response.append("\n\n🐛 디버그 정보:\n");
                response.append(errorOutput.toString());
            }

            return ResponseEntity.ok()
                    .header("Content-Type", "text/plain; charset=UTF-8")
                    .body(response.toString());

        } catch (Exception e) {
            log.error("Python 스크립트 실행 실패", e);
            return ResponseEntity.ok("❌ Python 실행 실패: " + e.getMessage());
        }
    }

    @GetMapping("/docker")
    public ResponseEntity<String> testDockerInfo() {
        StringBuilder result = new StringBuilder();
        result.append("🐳 시스템 환경 정보:\n\n");

        // 현재 디렉토리 확인
        result.append("현재 디렉토리: ").append(System.getProperty("user.dir")).append("\n");
        result.append("Java Version: ").append(System.getProperty("java.version")).append("\n");
        result.append("OS: ").append(System.getProperty("os.name")).append("\n\n");

        // 환경 변수 확인
        result.append("환경 변수:\n");
        result.append("- OPENAI_API_KEY: ").append(
                System.getenv("OPENAI_API_KEY") != null ? "✅ 설정됨" : "❌ 없음"
        ).append("\n\n");

        // 실행 환경 판단
        java.io.File dockerMarker = new java.io.File("/app");
        if (dockerMarker.exists()) {
            result.append("🐳 Docker 컨테이너 환경에서 실행 중\n");
        } else {
            result.append("🖥️ 로컬 환경에서 실행 중\n");
        }

        // 파일 시스템 확인
        result.append("\n파일 시스템 확인:\n");
        java.io.File currentDir = new java.io.File(".");
        java.io.File[] files = currentDir.listFiles();
        if (files != null) {
            result.append("현재 디렉토리 내용: ");
            for (java.io.File file : files) {
                if (file.isDirectory()) {
                    result.append("[").append(file.getName()).append("] ");
                }
            }
            result.append("\n");
        }

        return ResponseEntity.ok(result.toString());
    }
}