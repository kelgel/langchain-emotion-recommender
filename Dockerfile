FROM openjdk:17-jdk-slim

# Python 설치 (가상환경 제거)
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python 패키지 직접 설치
COPY ai-service/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
RUN pip3 install langchain-openai

WORKDIR /app

# Maven 설정
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .
RUN chmod +x mvnw && ./mvnw dependency:go-offline -B

# 소스 코드 및 빌드
COPY src ./src
RUN ./mvnw clean package -DskipTests -B

# 가상환경 관련 ENV 제거
EXPOSE 8080
CMD ["java", "-jar", "target/KDT_BE12_Toy_Project4-0.0.1-SNAPSHOT.jar"]