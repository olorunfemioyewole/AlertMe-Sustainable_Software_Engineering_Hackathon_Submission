# 🚨 Alert Me

Community-powered Security Intelligence for Nigeria

Alert Me is a multi-channel incident reporting platform that enables citizens to report suspicious activity through a mobile application, USSD, or emergency call centre. Reports are intelligently clustered and scored before being routed to law enforcement, allowing security agencies to prioritise response based on confidence rather than arrival order.

Built for the Sustainable Software Engineering Hackathon.

---

# Problem

Nigeria faces significant security challenges, yet citizens lack a simple, trusted way to report incidents. Existing systems are fragmented, inaccessible to many users, and provide little feedback to reporters.

Alert Me closes this gap by transforming community observations into actionable intelligence.

---

# Solution

Alert Me provides multiple reporting channels:

- 📱 Flutter Mobile Application
- ☎️ Emergency Call Centre Dashboard
- 📞 USSD Service
- 👮 Law Enforcement Dashboard

Every report contributes to a dynamic incident score based on:

- Incident severity
- Number of corroborating reports
- Reporter credibility
- Historical risk of the location

This enables responders to focus on the highest-confidence incidents first.

---

# Features

## Citizen

- Phone number authentication
- Anonymous reporting
- GPS assisted reporting
- Nearby incident alerts
- View report status

## Law Enforcement

- Ranked incident dashboard
- Incident confirmation
- Map visualisation
- Incident history

## Backend Intelligence

- Incident aggregation
- Confidence scoring
- Reputation system
- Hotspot detection
- Notification service

---

# Repository Structure

```
alert-me/

backend/
    FastAPI APIs

mobile/
    Flutter application

dashboard/
    Law enforcement web application

ussd/
    Africa's Talking USSD service

firebase/
    Firebase configuration

docs/
    Project documentation
```

---

# Architecture

```
                    Citizens
               ┌───────────────┐
               │               │
          Flutter App      USSD
               │               │
               └──────┬────────┘
                      │
                FastAPI Backend
                      │
       ┌──────────────┼──────────────┐
       │              │              │
 Firebase Auth   Firestore      FCM Push
                      │
             Law Enforcement Dashboard
```

---

# Technology Stack

## Mobile

- Flutter
- Riverpod
- GoRouter
- Dio

## Backend

- FastAPI
- Firebase Admin SDK

## Database

- Cloud Firestore

## Authentication

- Firebase Phone Authentication

## Notifications

- Firebase Cloud Messaging

## Mapping

- OpenStreetMap
- flutter_map

---

# MVP Scope

The initial MVP supports:

- Phone number login
- Incident reporting
- GPS capture
- Confidence scoring
- Officer confirmation
- Citizen notifications

---

# Getting Started

## Clone

```bash
git clone <repo>
cd alert-me
```

---

## Mobile

```bash
cd mobile
flutter pub get
flutter run
```

---

## Backend

```bash
cd backend
```

Follow the backend README for setup.

---

# Team

Built during the Sustainable Software Engineering Hackathon.