# 📈 Stock-Watch: 실시간 주식 시세 알림 및 대시보드

> **AWS EC2와 RDS를 활용한 실시간 주식 모니터링 및 자동 알림 시스템**

## 📌 1. 프로젝트 개요
* **목적**: 변동성이 큰 주식 시장에서 사용자가 설정한 목표가에 도달했을 때 실시간 알림을 제공하여 빠른 의사결정을 도움.
* **주요 기능**: 
    * `yfinance` 라이브러리를 이용한 전 세계(국내/해외) 주식 실시간 시세 수집
    * 사용자 설정 가격 도달 시 Discord Webhook을 통한 실시간 알림 발송
    * Streamlit 기반의 실시간 시세 대시보드 제공

## 🏗️ 2. AWS Architecture
* **Computing**: AWS EC2 (Ubuntu 24.04 LTS) - 데이터 수집 및 웹 서버 역할
* **Database**: AWS RDS (MySQL 8.0) - 주식 시세 이력 및 유저 설정값 저장
* **CI/CD**: GitHub Actions (Auto Deployment) - 코드 변경 시 EC2 자동 배포
* **Language**: Python 3.10+

## 🛠️ 3. 기술적 도전 및 해결
* **데이터 수집 전략**: 증권사 API의 복잡한 보안 인증 대신, 범용성이 높고 리눅스 환경에서 안정적인 `yfinance`를 활용하여 시스템 구축.
* **학생 계정 환경 최적화**: AWS Academy의 제한된 프리티어 리소스(t3.micro) 내에서 안정적인 운영을 위해 경량화된 Python 스크립트 작성.
* **보안 강화**: DB 접속 정보 및 Discord Webhook URL을 GitHub Actions의 `Secrets`로 관리하여 소스코드 유출 방지.

## 📊 프로젝트 발표 자료 (Google Slides)

<p align="center">
  <a href="https://docs.google.com/presentation/d/e/2PACX-1vSRaoJsz9Y-MksAKQ-IrFIFFAf4ukRBxVXwXm3UlyzriYu5d3196b8Fd1SAco1FLKF33eYgvASO07pV/pub">
    <img src="https://img.shields.io/badge/Check%20Presentation-Click%20Here-orange?style=for-the-badge&logo=googleslides" alt="Google Slides" />
    <br>
    <img src="https://via.placeholder.com/800x450.png?text=Stock-Watch+Presentation+Slide+Screenshot" alt="Stock-Watch Presentation" width="800">
  </a>
  <br>
</p>

![bandicam2026-02-2309-50-24-456-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/0395e5b0-3887-4e71-bd31-420c44683a37)
