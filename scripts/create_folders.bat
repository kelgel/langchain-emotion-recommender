@echo off
echo Creating folders...

REM ai-service/app 하위 폴더들
mkdir ai-service\app\agents
mkdir ai-service\app\main_agent
mkdir ai-service\app\tools
mkdir ai-service\app\chains
mkdir ai-service\app\prompts
mkdir ai-service\app\models
mkdir ai-service\app\utils
mkdir ai-service\app\config

REM data 관련 폴더들
mkdir ai-service\data\chroma_db
mkdir ai-service\data\embeddings
echo Done!